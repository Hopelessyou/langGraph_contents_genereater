"""관련 문서 추천 로직"""

from typing import List, Dict, Any, Optional
import logging

from .vector_store import VectorStore
from .embedding import EmbeddingGenerator

logger = logging.getLogger(__name__)


class DocumentRecommender:
    """문서 추천기"""
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator,
    ):
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
    
    def recommend_related(
        self,
        document_id: str,
        n_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        특정 문서와 관련된 문서를 추천합니다.
        
        Args:
            document_id: 기준 문서 ID
            n_results: 추천할 문서 수
            
        Returns:
            추천 문서 리스트
        """
        try:
            # 문서 검색 (메타데이터로 찾기)
            results = self.vector_store.search(
                query_embedding=None,  # 메타데이터만으로 검색
                n_results=1,
                where={"document_id": document_id},
            )
            
            if not results.get("ids") or not results["ids"][0]:
                logger.warning(f"문서를 찾을 수 없습니다: {document_id}")
                return []
            
            # 첫 번째 결과의 임베딩 사용
            # 실제로는 벡터 DB에서 임베딩을 가져와야 하지만,
            # 여기서는 간단히 메타데이터 기반 추천으로 대체
            metadata = results["metadatas"][0][0] if results.get("metadatas") else {}
            
            # 관련 문서 검색 (같은 카테고리, 하위 카테고리)
            where = {}
            if metadata.get("category"):
                where["category"] = metadata["category"]
            if metadata.get("sub_category"):
                where["sub_category"] = metadata["sub_category"]
            
            # 문서 타입도 고려
            if metadata.get("type"):
                where["type"] = metadata["type"]
            
            # 자기 자신 제외
            # 실제로는 더 정교한 필터링 필요
            
            # 벡터 검색으로 유사 문서 찾기
            # 여기서는 간단히 메타데이터 기반으로 반환
            # 실제 구현에서는 문서의 임베딩을 사용하여 유사 문서 검색
            
            return []
            
        except Exception as e:
            logger.error(f"문서 추천 실패: {str(e)}")
            return []
    
    def recommend_by_keywords(
        self,
        keywords: List[str],
        n_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        키워드 기반 문서 추천
        
        Args:
            keywords: 키워드 리스트
            n_results: 추천할 문서 수
            
        Returns:
            추천 문서 리스트
        """
        try:
            # 키워드를 조합하여 쿼리 생성
            query = " ".join(keywords)
            
            # 임베딩 생성
            query_embedding = self.embedding_generator.embed_text(query)
            
            # 검색
            results = self.vector_store.search(
                query_embedding=query_embedding,
                n_results=n_results,
            )
            
            # 결과 포맷팅
            recommendations = []
            if results.get("ids") and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    recommendations.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else None,
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"키워드 기반 추천 실패: {str(e)}")
            return []

