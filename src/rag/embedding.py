"""임베딩 생성 및 관리"""

from typing import List, Optional
import logging

try:
    from langchain_openai import OpenAIEmbeddings
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """임베딩 생성기"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.embedding_model
        self.embeddings = None
        self._initialize()
    
    def _initialize(self):
        """임베딩 모델 초기화"""
        if not OPENAI_AVAILABLE:
            raise ImportError("langchain-openai가 설치되지 않았습니다.")
        
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        self.embeddings = OpenAIEmbeddings(
            model=self.model_name,
            openai_api_key=settings.openai_api_key,
        )
        logger.info(f"임베딩 모델 초기화: {self.model_name}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        단일 텍스트를 임베딩합니다.
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터
        """
        try:
            result = self.embeddings.embed_query(text)
            return result
        except Exception as e:
            logger.error(f"임베딩 생성 실패: {str(e)}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        여러 텍스트를 일괄 임베딩합니다.
        
        Args:
            texts: 임베딩할 텍스트 리스트
            
        Returns:
            임베딩 벡터 리스트
        """
        try:
            results = self.embeddings.embed_documents(texts)
            return results
        except Exception as e:
            logger.error(f"일괄 임베딩 생성 실패: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """임베딩 차원을 반환합니다."""
        # text-embedding-3-large는 3072차원
        if "3-large" in self.model_name:
            return 3072
        elif "3-small" in self.model_name:
            return 1536
        else:
            # 기본값 (ada-002 등)
            return 1536

