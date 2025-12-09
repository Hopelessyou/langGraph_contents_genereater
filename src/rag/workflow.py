"""LangGraph 워크플로우 - 검색 및 질의응답"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import logging
import asyncio

from .vector_store import VectorStore
from .embedding import EmbeddingGenerator
from config.settings import settings

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """워크플로우 상태"""
    query: str
    query_embedding: Optional[List[float]]
    search_results: List[Dict[str, Any]]
    filtered_results: List[Dict[str, Any]]
    reranked_results: List[Dict[str, Any]]
    context: str
    response: Optional[str]
    metadata_filters: Optional[Dict[str, Any]]
    document_types: Optional[List[str]]
    error: Optional[str]


class RAGWorkflow:
    """RAG 워크플로우 관리자"""
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator,
    ):
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """워크플로우 그래프 구성"""
        workflow = StateGraph(GraphState)
        
        # 노드 추가
        workflow.add_node("analyze_query", self._analyze_query_node)
        workflow.add_node("vector_search", self._vector_search_node)
        workflow.add_node("filter_metadata", self._filter_metadata_node)
        workflow.add_node("rerank_results", self._rerank_results_node)
        workflow.add_node("build_context", self._build_context_node)
        
        # 엣지 정의
        workflow.set_entry_point("analyze_query")
        workflow.add_edge("analyze_query", "vector_search")
        workflow.add_edge("vector_search", "filter_metadata")
        workflow.add_edge("filter_metadata", "rerank_results")
        workflow.add_edge("rerank_results", "build_context")
        workflow.add_edge("build_context", END)
        
        return workflow.compile()
    
    def _analyze_query_node(self, state: GraphState) -> GraphState:
        """쿼리 분석 노드"""
        try:
            query = state.get("query", "")
            
            # 쿼리 임베딩 생성 (비동기 메서드를 동기적으로 실행)
            # LangGraph는 동기적으로 실행되므로, 새 이벤트 루프를 생성하여 실행
            try:
                # 이미 실행 중인 루프가 있는지 확인
                loop = asyncio.get_running_loop()
                # 실행 중인 루프가 있으면 새 스레드에서 새 루프 생성
                import concurrent.futures
                def run_in_new_loop():
                    return asyncio.run(self.embedding_generator.embed_text(query))
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_new_loop)
                    query_embedding = future.result()
            except RuntimeError:
                # 이벤트 루프가 없으면 새로 생성
                query_embedding = asyncio.run(
                    self.embedding_generator.embed_text(query)
                )
            
            # 메타데이터 필터 추출 (간단한 키워드 기반 + 사건번호 추출)
            extracted_filters = self._extract_filters(query)
            
            # 외부에서 전달된 필터와 병합 (외부 필터가 우선)
            external_filters = state.get("metadata_filters")
            if external_filters:
                # 외부 필터가 있으면 병합 (외부 필터 우선)
                metadata_filters = {**extracted_filters, **external_filters}
            else:
                metadata_filters = extracted_filters if extracted_filters else None
            
            # 문서 타입 추출
            # 외부에서 전달된 document_types가 있으면 사용, 없으면 쿼리에서 추출
            external_doc_types = state.get("document_types")
            valid_document_types = {"case", "statute", "procedure", "template"}
            if external_doc_types:
                # "string"이 포함되어 있으면 모든 타입 검색 (필터링 없음)
                if "string" in external_doc_types:
                    document_types = None  # 모든 타입 검색
                else:
                    # 유효한 문서 타입만 사용
                    document_types = [dt for dt in external_doc_types if dt in valid_document_types]
                    if not document_types:  # 유효한 타입이 없으면 쿼리에서 추출
                        document_types = self._extract_document_types(query)
            else:
                document_types = self._extract_document_types(query)
            
            state["query_embedding"] = query_embedding
            state["metadata_filters"] = metadata_filters
            state["document_types"] = document_types
            
            logger.debug(f"쿼리 분석 완료: {query[:50]}...")
            
        except Exception as e:
            logger.error(f"쿼리 분석 실패: {str(e)}")
            state["error"] = f"쿼리 분석 실패: {str(e)}"
        
        return state
    
    def _vector_search_node(self, state: GraphState) -> GraphState:
        """벡터 검색 노드"""
        try:
            query_embedding = state.get("query_embedding")
            if not query_embedding:
                state["error"] = "쿼리 임베딩이 없습니다."
                return state
            
            # 검색 수행 (동기 메서드 직접 호출)
            n_results = settings.search_default_top_k
            metadata_filters = state.get("metadata_filters", {})
            
            # ChromaDB where 절 구성
            # 사건번호가 있으면 정확한 매칭으로 검색 범위 축소
            where = None
            if metadata_filters:
                # ChromaDB where 절 형식으로 변환 (단순 형식 사용)
                # 단일 조건: {"case_number": "2005고합694"}
                # 여러 조건: {"$and": [{"case_number": "2005고합694"}, {"category": "형사"}]}
                where_conditions = {}
                for key, value in metadata_filters.items():
                    if value:  # None이 아닌 경우만
                        where_conditions[key] = value
                
                if where_conditions:
                    # 단일 조건이면 단순 형식, 여러 조건이면 $and 사용
                    if len(where_conditions) == 1:
                        where = where_conditions
                    else:
                        # 여러 조건을 $and로 결합
                        and_conditions = [{k: v} for k, v in where_conditions.items()]
                        where = {"$and": and_conditions}
                    logger.info(f"ChromaDB where 절: {where}")
            else:
                logger.debug("메타데이터 필터가 없어 where 절을 사용하지 않음")
            
            # vector_store.search()는 동기 메서드이므로 직접 호출
            results = self.vector_store.search(
                query_embedding=query_embedding,
                n_results=n_results,
                where=where,
            )
            
            # 결과 포맷팅
            search_results = []
            if results.get("ids") and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    search_results.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else None,
                    })
            
            state["search_results"] = search_results
            logger.info(f"벡터 검색 완료: {len(search_results)}개 결과 (where: {where})")
            
        except Exception as e:
            logger.error(f"벡터 검색 실패: {str(e)}")
            state["error"] = f"벡터 검색 실패: {str(e)}"
            state["search_results"] = []
        
        return state
    
    def _filter_metadata_node(self, state: GraphState) -> GraphState:
        """메타데이터 필터링 노드"""
        try:
            search_results = state.get("search_results", [])
            document_types = state.get("document_types")
            metadata_filters = state.get("metadata_filters", {})
            
            filtered_results = search_results.copy()
            
            # 문서 타입 필터링
            # 유효한 문서 타입만 필터링 (case, statute, procedure, template)
            valid_document_types = {"case", "statute", "procedure", "template"}
            if document_types:
                # "string"이 포함되어 있으면 모든 타입 검색 (필터링 없음)
                if "string" in document_types:
                    # 필터링하지 않음 (모든 결과 반환)
                    pass
                else:
                    # 유효한 타입만 필터링
                    valid_types = [dt for dt in document_types if dt in valid_document_types]
                    if valid_types:
                        filtered_results = [
                            r for r in filtered_results
                            if r.get("metadata", {}).get("type") in valid_types
                        ]
                    # 유효하지 않은 타입만 있으면 필터링하지 않음 (모든 결과 반환)
            
            # 추가 메타데이터 필터링
            if metadata_filters:
                for key, value in metadata_filters.items():
                    if key != "type":  # 타입은 이미 필터링됨
                        filtered_results = [
                            r for r in filtered_results
                            if r.get("metadata", {}).get(key) == value
                        ]
            
            state["filtered_results"] = filtered_results
            logger.debug(f"메타데이터 필터링 완료: {len(filtered_results)}개 결과")
            
        except Exception as e:
            logger.error(f"메타데이터 필터링 실패: {str(e)}")
            state["error"] = f"메타데이터 필터링 실패: {str(e)}"
            state["filtered_results"] = state.get("search_results", [])
        
        return state
    
    def _rerank_results_node(self, state: GraphState) -> GraphState:
        """결과 재랭킹 노드"""
        try:
            filtered_results = state.get("filtered_results", [])
            query = state.get("query", "")
            
            # 거리 기반 정렬 (작을수록 유사)
            reranked = sorted(
                filtered_results,
                key=lambda x: x.get("distance", float("inf"))
            )
            
            # 상위 결과만 선택
            reranked = reranked[:settings.search_rerank_top_k]
            
            state["reranked_results"] = reranked
            logger.debug(f"재랭킹 완료: {len(reranked)}개 결과")
            
        except Exception as e:
            logger.error(f"재랭킹 실패: {str(e)}")
            state["error"] = f"재랭킹 실패: {str(e)}"
            state["reranked_results"] = state.get("filtered_results", [])[:settings.search_rerank_top_k]
        
        return state
    
    def _build_context_node(self, state: GraphState) -> GraphState:
        """컨텍스트 구성 노드"""
        try:
            reranked_results = state.get("reranked_results", [])
            
            # 컨텍스트 구성
            context_parts = []
            for i, result in enumerate(reranked_results, 1):
                doc_text = result.get("document", "")
                metadata = result.get("metadata", {})
                
                context_parts.append(
                    f"[문서 {i}]\n"
                    f"제목: {metadata.get('title', 'N/A')}\n"
                    f"타입: {metadata.get('type', 'N/A')}\n"
                    f"내용: {doc_text}\n"
                )
            
            context = "\n".join(context_parts)
            state["context"] = context
            
            logger.debug(f"컨텍스트 구성 완료: {len(context)}자")
            
        except Exception as e:
            logger.error(f"컨텍스트 구성 실패: {str(e)}")
            state["error"] = f"컨텍스트 구성 실패: {str(e)}"
            state["context"] = ""
        
        return state
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        """쿼리에서 필터 추출"""
        import re
        filters = {}
        
        # 간단한 키워드 기반 필터 추출
        if "형사" in query:
            filters["category"] = "형사"
        elif "민사" in query:
            filters["category"] = "민사"
        
        if "사기" in query:
            filters["sub_category"] = "사기"
        
        # 사건번호 패턴 추출 (예: 2005고합694, 2010도2810 등)
        # 패턴: 4자리 숫자 + 한글(1자 이상) + 숫자(1자 이상)
        # 공백을 제거한 후 매칭 시도
        query_no_spaces = query.replace(" ", "").replace("\t", "")
        case_number_pattern = r'(\d{4}[가-힣]+\d+)'
        case_number_matches = re.findall(case_number_pattern, query_no_spaces)
        if case_number_matches:
            # 첫 번째 매칭된 사건번호 사용
            filters["case_number"] = case_number_matches[0]
            logger.info(f"쿼리에서 사건번호 추출: {case_number_matches[0]} (원본 쿼리: {query[:50]})")
        else:
            # 공백이 있는 경우에도 시도 (예: "2005 고합 694")
            case_number_pattern_with_spaces = r'(\d{4})\s*([가-힣]+)\s*(\d+)'
            spaced_matches = re.findall(case_number_pattern_with_spaces, query)
            if spaced_matches:
                # 공백 제거하여 결합
                case_number = ''.join(spaced_matches[0])
                filters["case_number"] = case_number
                logger.info(f"쿼리에서 사건번호 추출 (공백 포함): {case_number} (원본 쿼리: {query[:50]})")
        
        return filters
    
    def _extract_document_types(self, query: str) -> Optional[List[str]]:
        """쿼리에서 문서 타입 추출"""
        types = []
        
        if "법령" in query or "조문" in query:
            types.append("statute")
        if "판례" in query or "판결" in query:
            types.append("case")
        if "절차" in query:
            types.append("procedure")
        if "템플릿" in query:
            types.append("template")
        
        return types if types else None
    
    def run(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        워크플로우 실행
        
        Args:
            query: 사용자 쿼리
            **kwargs: 추가 옵션
            
        Returns:
            실행 결과
        """
        initial_state: GraphState = {
            "query": query,
            "query_embedding": None,
            "search_results": [],
            "filtered_results": [],
            "reranked_results": [],
            "context": "",
            "response": None,
            "metadata_filters": None,
            "document_types": None,
            "error": None,
        }
        
        # 추가 옵션 병합
        initial_state.update(kwargs)
        
        # 워크플로우 실행
        final_state = self.graph.invoke(initial_state)
        
        return final_state

