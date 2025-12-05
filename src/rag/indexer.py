"""벡터 DB 인덱싱 파이프라인"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from ..models import BaseDocument
from ..processors.validator import DocumentValidator
from .vector_store import VectorStore
from .embedding import EmbeddingGenerator
from .chunker import TextChunker

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """문서 인덱싱 파이프라인"""
    
    def __init__(
        self,
        collection_name: str = "legal_documents",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.validator = DocumentValidator()
        self.vector_store = VectorStore(collection_name=collection_name)
        self.embedding_generator = EmbeddingGenerator()
        self.chunker = TextChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    
    def index_document(self, document: BaseDocument, chunk: bool = True) -> Dict[str, Any]:
        """
        단일 문서를 인덱싱합니다.
        
        Args:
            document: 인덱싱할 문서
            chunk: 청킹 여부
            
        Returns:
            인덱싱 결과
        """
        try:
            # 청킹
            if chunk:
                chunks = self.chunker.chunk_document(document)
            else:
                # 청킹 없이 전체 문서를 하나의 청크로
                if isinstance(document.content, str):
                    text = document.content
                elif isinstance(document.content, list):
                    text = "\n".join(document.content)
                else:
                    text = str(document.content)
                
                chunks = [{
                    "text": text,
                    "metadata": {
                        "chunk_index": 0,
                        "document_id": document.id,
                        "document_type": document.type,
                    }
                }]
            
            # 임베딩 생성
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedding_generator.embed_texts(texts)
            
            # 문서 객체 생성 (청크별)
            chunk_documents = []
            for i, chunk_data in enumerate(chunks):
                chunk_doc = BaseDocument(
                    id=f"{document.id}_chunk_{i}",
                    category=document.category,
                    sub_category=document.sub_category,
                    type=document.type,
                    title=f"{document.title} (청크 {i+1})",
                    content=chunk_data["text"],
                    metadata={
                        **document.metadata,
                        **chunk_data["metadata"],
                    }
                )
                chunk_documents.append(chunk_doc)
            
            # 벡터 DB에 추가
            ids = self.vector_store.add_documents(
                documents=chunk_documents,
                embeddings=embeddings,
            )
            
            return {
                "success": True,
                "document_id": document.id,
                "chunks_count": len(chunks),
                "indexed_ids": ids,
            }
            
        except Exception as e:
            logger.error(f"문서 인덱싱 실패: {document.id} - {str(e)}")
            return {
                "success": False,
                "document_id": document.id,
                "error": str(e),
            }
    
    def index_file(self, file_path: Path | str, chunk: bool = True) -> Dict[str, Any]:
        """
        JSON 파일을 읽어서 인덱싱합니다.
        
        Args:
            file_path: JSON 파일 경로
            chunk: 청킹 여부
            
        Returns:
            인덱싱 결과
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "success": False,
                "error": f"파일이 존재하지 않습니다: {file_path}",
            }
        
        try:
            # JSON 파일 읽기
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 검증
            success, model = self.validator.validate(data)
            if not success:
                return {
                    "success": False,
                    "error": f"검증 실패: {', '.join(self.validator.get_errors())}",
                }
            
            # 인덱싱
            return self.index_document(model, chunk=chunk)
            
        except Exception as e:
            logger.error(f"파일 인덱싱 실패: {file_path} - {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def index_directory(
        self,
        directory: Path | str,
        pattern: str = "*.json",
        chunk: bool = True,
        recursive: bool = True,
    ) -> Dict[str, Any]:
        """
        디렉토리 내 모든 JSON 파일을 인덱싱합니다.
        
        Args:
            directory: 디렉토리 경로
            pattern: 파일 패턴
            chunk: 청킹 여부
            recursive: 하위 디렉토리 재귀 검색 여부 (기본값: True)
            
        Returns:
            일괄 인덱싱 결과
        """
        directory = Path(directory)
        results = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "details": [],
        }
        
        # 재귀 검색 여부에 따라 glob 또는 rglob 사용
        if recursive:
            file_paths = directory.rglob(pattern)
        else:
            file_paths = directory.glob(pattern)
        
        for file_path in file_paths:
            # 디렉토리는 제외하고 파일만 처리
            if not file_path.is_file():
                continue
                
            results["total"] += 1
            result = self.index_file(file_path, chunk=chunk)
            
            if result["success"]:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "file": str(file_path.relative_to(directory)),  # 상대 경로 포함
                "result": result,
            })
        
        logger.info(
            f"디렉토리 인덱싱 완료: 총 {results['total']}건, "
            f"성공 {results['success']}건, 실패 {results['failed']}건"
        )
        
        return results
    
    def get_index_status(self) -> Dict[str, Any]:
        """인덱스 상태를 반환합니다."""
        return {
            "collection_name": self.vector_store.collection_name,
            "document_count": self.vector_store.get_count(),
        }

