"""텍스트 청킹 전략"""

from typing import List, Dict, Any
from ..models import BaseDocument
import logging

logger = logging.getLogger(__name__)


class TextChunker:
    """텍스트 청킹 클래스"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_document(self, document: BaseDocument) -> List[Dict[str, Any]]:
        """
        문서를 청크로 분할합니다.
        
        Args:
            document: 분할할 문서
            
        Returns:
            청크 리스트 (각 청크는 {text, metadata} 딕셔너리)
        """
        # 타입별 청킹 전략 선택
        if document.type == "statute":
            return self._chunk_statute(document)
        elif document.type == "case":
            return self._chunk_case(document)
        elif document.type == "template":
            return self._chunk_template(document)
        else:
            return self._chunk_default(document)
    
    def _chunk_statute(self, document: BaseDocument) -> List[Dict[str, Any]]:
        """법령 문서 청킹 (조문 단위로 분할)"""
        chunks = []
        
        if isinstance(document.content, str):
            # 조문 번호로 분할 시도
            content = document.content
            # 조문 패턴: ①, ②, ③ 등 또는 1), 2), 3) 등
            import re
            pattern = r'[①-⑳]|\(\d+\)'
            parts = re.split(pattern, content)
            
            if len(parts) > 1:
                # 조문별로 분할
                for i, part in enumerate(parts[1:], 1):  # 첫 번째는 빈 문자열일 수 있음
                    if part.strip():
                        chunks.append({
                            "text": part.strip(),
                            "metadata": {
                                "chunk_index": i,
                                "document_id": document.id,
                                "document_type": document.type,
                                "article_number": document.metadata.get("article_number", ""),
                            }
                        })
            else:
                # 조문 분할 실패 시 기본 청킹
                chunks = self._chunk_default(document)
        else:
            chunks = self._chunk_default(document)
        
        return chunks
    
    def _chunk_case(self, document: BaseDocument) -> List[Dict[str, Any]]:
        """판례 문서 청킹"""
        chunks = []
        
        if isinstance(document.content, str):
            content = document.content
            
            # 판례는 보통 짧으므로 전체를 하나의 청크로
            # 또는 문장 단위로 분할
            sentences = content.split('。')  # 한국어 문장 구분자
            current_chunk = ""
            chunk_index = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                if len(current_chunk) + len(sentence) > self.chunk_size:
                    if current_chunk:
                        chunks.append({
                            "text": current_chunk.strip(),
                            "metadata": {
                                "chunk_index": chunk_index,
                                "document_id": document.id,
                                "document_type": document.type,
                            }
                        })
                        chunk_index += 1
                    current_chunk = sentence
                else:
                    current_chunk += " " + sentence if current_chunk else sentence
            
            # 마지막 청크 추가
            if current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "metadata": {
                        "chunk_index": chunk_index,
                        "document_id": document.id,
                        "document_type": document.type,
                    }
                })
        else:
            chunks = self._chunk_default(document)
        
        return chunks
    
    def _chunk_template(self, document: BaseDocument) -> List[Dict[str, Any]]:
        """템플릿 문서 청킹 (각 항목을 별도 청크로)"""
        chunks = []
        
        if isinstance(document.content, list):
            for i, item in enumerate(document.content):
                chunks.append({
                    "text": str(item),
                    "metadata": {
                        "chunk_index": i,
                        "document_id": document.id,
                        "document_type": document.type,
                    }
                })
        else:
            chunks = self._chunk_default(document)
        
        return chunks
    
    def _chunk_default(self, document: BaseDocument) -> List[Dict[str, Any]]:
        """기본 청킹 전략 (고정 크기로 분할)"""
        chunks = []
        
        # 텍스트 추출
        if isinstance(document.content, str):
            text = document.content
        elif isinstance(document.content, list):
            text = "\n".join(str(item) for item in document.content)
        else:
            text = str(document.content)
        
        # 고정 크기로 분할
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # 오버랩 처리
            if end < len(text) and self.chunk_overlap > 0:
                # 다음 청크 시작점을 오버랩만큼 앞으로
                end = end - self.chunk_overlap
            
            chunks.append({
                "text": chunk_text.strip(),
                "metadata": {
                    "chunk_index": chunk_index,
                    "document_id": document.id,
                    "document_type": document.type,
                }
            })
            
            chunk_index += 1
            start = end if end > start else start + self.chunk_size
        
        return chunks

