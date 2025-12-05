"""벡터 DB 관리"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from ..models import BaseDocument
from config.settings import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """벡터 DB 관리 클래스"""
    
    def __init__(self, collection_name: str = "legal_documents"):
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._initialize()
    
    def _initialize(self):
        """벡터 DB 초기화"""
        if settings.vector_db_type == "chroma":
            if not CHROMA_AVAILABLE:
                raise ImportError("chromadb가 설치되지 않았습니다. pip install chromadb를 실행하세요.")
            
            self.client = chromadb.PersistentClient(
                path=str(settings.chroma_persist_path),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )
            
            # 컬렉션 생성 또는 가져오기
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                logger.info(f"기존 컬렉션 로드: {self.collection_name}")
            except Exception:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "법률 문서 벡터 저장소"}
                )
                logger.info(f"새 컬렉션 생성: {self.collection_name}")
        else:
            raise ValueError(f"지원하지 않는 벡터 DB 타입: {settings.vector_db_type}")
    
    def add_documents(
        self,
        documents: List[BaseDocument],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        문서를 벡터 DB에 추가합니다.
        
        Args:
            documents: 추가할 문서 리스트
            embeddings: 문서 임베딩 리스트
            metadatas: 메타데이터 리스트 (선택)
            
        Returns:
            추가된 문서 ID 리스트
        """
        if len(documents) != len(embeddings):
            raise ValueError("문서와 임베딩의 개수가 일치하지 않습니다.")
        
        ids = [doc.id for doc in documents]
        texts = []
        metadata_list = []
        
        for doc in documents:
            # 텍스트 추출
            if isinstance(doc.content, str):
                text = doc.content
            elif isinstance(doc.content, list):
                text = "\n".join(doc.content)
            else:
                text = str(doc.content)
            
            texts.append(text)
            
            # 메타데이터 구성
            metadata = {
                "id": doc.id,
                "category": doc.category,
                "sub_category": doc.sub_category,
                "type": doc.type,
                "title": doc.title,
            }
            
            # 추가 메타데이터 병합
            if doc.metadata:
                metadata.update(doc.metadata)
            
            metadata_list.append(metadata)
        
        # 메타데이터 병합
        if metadatas:
            for i, meta in enumerate(metadatas):
                if i < len(metadata_list):
                    metadata_list[i].update(meta)
        
        # 벡터 DB에 추가
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadata_list,
        )
        
        logger.info(f"{len(documents)}개 문서를 벡터 DB에 추가했습니다.")
        return ids
    
    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        벡터 검색을 수행합니다.
        
        Args:
            query_embedding: 쿼리 임베딩
            n_results: 반환할 결과 개수
            where: 메타데이터 필터 조건
            
        Returns:
            검색 결과 딕셔너리
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )
        
        return results
    
    def delete(self, ids: Optional[List[str]] = None, where: Optional[Dict[str, Any]] = None):
        """
        문서를 삭제합니다.
        
        Args:
            ids: 삭제할 문서 ID 리스트
            where: 삭제할 문서 필터 조건
        """
        self.collection.delete(ids=ids, where=where)
        logger.info(f"문서 삭제 완료: ids={ids}, where={where}")
    
    def update(
        self,
        ids: List[str],
        embeddings: Optional[List[List[float]]] = None,
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        문서를 업데이트합니다.
        
        Args:
            ids: 업데이트할 문서 ID 리스트
            embeddings: 새로운 임베딩 (선택)
            documents: 새로운 문서 내용 (선택)
            metadatas: 새로운 메타데이터 (선택)
        """
        self.collection.update(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        logger.info(f"{len(ids)}개 문서를 업데이트했습니다.")
    
    def get_count(self) -> int:
        """컬렉션의 문서 개수를 반환합니다."""
        return self.collection.count()
    
    def reset(self):
        """컬렉션을 초기화합니다."""
        self.client.delete_collection(name=self.collection_name)
        self._initialize()
        logger.info(f"컬렉션 '{self.collection_name}'을 초기화했습니다.")

