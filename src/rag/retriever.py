"""검색 및 검색 강화 모듈"""

from typing import List, Dict, Any, Optional
import logging
import asyncio

from .vector_store import VectorStore
from .embedding import EmbeddingGenerator
from .workflow import RAGWorkflow

logger = logging.getLogger(__name__)


class HybridRetriever:
    """하이브리드 검색 (벡터 + 키워드)"""
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator,
    ):
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.workflow = RAGWorkflow(vector_store, embedding_generator)
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        document_types: Optional[List[str]] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        하이브리드 검색 수행
        
        Args:
            query: 검색 쿼리
            n_results: 반환할 결과 수
            document_types: 문서 타입 필터
            metadata_filters: 메타데이터 필터
            
        Returns:
            검색 결과
        """
        try:
            # 워크플로우 실행 (동기 함수를 비동기로 실행)
            result = await asyncio.to_thread(
                self.workflow.run,
                query=query,
                metadata_filters=metadata_filters,
                document_types=document_types,
            )
            
            # 결과 제한
            reranked = result.get("reranked_results", [])[:n_results]
            
            return {
                "query": query,
                "results": reranked,
                "total": len(reranked),
                "context": result.get("context", ""),
                "error": result.get("error"),
            }
            
        except Exception as e:
            logger.error(f"검색 실패: {str(e)}")
            return {
                "query": query,
                "results": [],
                "total": 0,
                "context": "",
                "error": str(e),
            }
    
    def rerank_results(
        self,
        results: List[Dict[str, Any]],
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        검색 결과 재랭킹
        
        Args:
            results: 검색 결과 리스트
            query: 원본 쿼리
            top_k: 상위 k개 반환
            
        Returns:
            재랭킹된 결과
        """
        if not results:
            return []
        
        # 거리 기반 정렬 (이미 워크플로우에서 처리됨)
        # 여기서는 추가적인 재랭킹 로직 구현 가능
        
        # 간단한 점수 계산 (거리 기반)
        for result in results:
            distance = result.get("distance", float("inf"))
            # 거리를 점수로 변환 (작을수록 높은 점수)
            result["score"] = 1.0 / (1.0 + distance) if distance > 0 else 1.0
        
        # 점수 순으로 정렬
        reranked = sorted(
            results,
            key=lambda x: x.get("score", 0),
            reverse=True,
        )
        
        return reranked[:top_k]

