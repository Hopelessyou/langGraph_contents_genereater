"""LangGraph 워크플로우 - 검색 및 질의응답"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import logging

from .vector_store import VectorStore
from .embedding import EmbeddingGenerator

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
            
            # 쿼리 임베딩 생성
            query_embedding = self.embedding_generator.embed_text(query)
            
            # 메타데이터 필터 추출 (간단한 키워드 기반)
            metadata_filters = self._extract_filters(query)
            
            # 문서 타입 추출
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
            
            # 검색 수행
            n_results = 10  # 초기 검색 결과 수
            where = state.get("metadata_filters")
            
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
            logger.debug(f"벡터 검색 완료: {len(search_results)}개 결과")
            
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
            if document_types:
                filtered_results = [
                    r for r in filtered_results
                    if r.get("metadata", {}).get("type") in document_types
                ]
            
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
            
            # 상위 5개만 선택
            reranked = reranked[:5]
            
            state["reranked_results"] = reranked
            logger.debug(f"재랭킹 완료: {len(reranked)}개 결과")
            
        except Exception as e:
            logger.error(f"재랭킹 실패: {str(e)}")
            state["error"] = f"재랭킹 실패: {str(e)}"
            state["reranked_results"] = state.get("filtered_results", [])[:5]
        
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
        filters = {}
        
        # 간단한 키워드 기반 필터 추출
        if "형사" in query:
            filters["category"] = "형사"
        elif "민사" in query:
            filters["category"] = "민사"
        
        if "사기" in query:
            filters["sub_category"] = "사기"
        
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

