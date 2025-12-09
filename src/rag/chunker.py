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
    
    def chunk_document(
        self, 
        document: BaseDocument,
        split_statute_by_items: bool = False
    ) -> List[Dict[str, Any]]:
        """
        문서를 청크로 분할합니다.
        
        Args:
            document: 분할할 문서
            split_statute_by_items: 법령 문서의 경우 조문 내 항목 단위로도 분할할지 여부
            
        Returns:
            청크 리스트 (각 청크는 {text, metadata} 딕셔너리)
        """
        # 타입별 청킹 전략 선택
        if document.type == "statute":
            return self._chunk_statute(document, split_by_items=split_statute_by_items)
        elif document.type == "case":
            return self._chunk_case(document)
        elif document.type == "template":
            return self._chunk_template(document)
        else:
            return self._chunk_default(document)
    
    def _chunk_statute(
        self, 
        document: BaseDocument,
        split_by_items: bool = False
    ) -> List[Dict[str, Any]]:
        """
        법령 문서 청킹 (조문 단위로 정확히 분할)
        
        Args:
            document: 분할할 법령 문서
            split_by_items: True이면 조문 내 항목(①②③) 단위로도 분할
        """
        chunks = []
        import re
        
        if isinstance(document.content, str):
            content = document.content
            
            # 조문 패턴: "제X조", "제X조의2", "제X조의3" 등
            # 예: "제1조", "제2조", "제347조", "제1조의2"
            article_pattern = r'제\s*(\d+)\s*조(?:\s*의\s*(\d+))?'
            
            # 조문 위치 찾기
            article_matches = list(re.finditer(article_pattern, content))
            
            if len(article_matches) > 0:
                # 조문별로 분할
                for i, match in enumerate(article_matches):
                    article_num = match.group(1)
                    sub_article = match.group(2) if match.group(2) else None
                    
                    # 다음 조문까지의 텍스트 추출
                    start_pos = match.start()
                    if i + 1 < len(article_matches):
                        end_pos = article_matches[i + 1].start()
                    else:
                        end_pos = len(content)
                    
                    article_text = content[start_pos:end_pos].strip()
                    
                    if not article_text:
                        continue
                    
                    # 조문 번호 구성
                    article_number = f"제{article_num}조"
                    if sub_article:
                        article_number += f"의{sub_article}"
                    
                    # 항목 단위 분할 여부
                    if split_by_items:
                        # 조문 내 항목(①②③) 단위로 분할
                        item_chunks = self._split_article_by_items(
                            article_text, 
                            article_number,
                            document
                        )
                        chunks.extend(item_chunks)
                    else:
                        # 조문 전체를 하나의 청크로
                        chunks.append({
                            "text": article_text,
                            "metadata": {
                                "chunk_index": len(chunks),
                                "document_id": document.id,
                                "document_type": document.type,
                                "article_number": article_number,
                                "article_num": int(article_num),
                                "sub_article": int(sub_article) if sub_article else None,
                            }
                        })
            else:
                # 조문 패턴을 찾지 못한 경우 기본 청킹
                logger.warning(f"조문 패턴을 찾지 못했습니다. 기본 청킹 사용: {document.id}")
                chunks = self._chunk_default(document)
        else:
            chunks = self._chunk_default(document)
        
        return chunks
    
    def _split_article_by_items(
        self,
        article_text: str,
        article_number: str,
        document: BaseDocument
    ) -> List[Dict[str, Any]]:
        """
        조문을 항목(①②③) 단위로 분할
        
        Args:
            article_text: 조문 텍스트
            article_number: 조문 번호 (예: "제1조")
            document: 원본 문서
            
        Returns:
            항목별 청크 리스트
        """
        chunks = []
        import re
        
        # 항목 패턴: ①, ②, ③, ④, ⑤, ⑥, ⑦, ⑧, ⑨, ⑩, ⑪, ⑫, ⑬, ⑭, ⑮, ⑯, ⑰, ⑱, ⑲, ⑳
        # 또는 (1), (2), (3) 등
        item_pattern = r'([①-⑳]|\(\d+\))'
        
        # 항목 위치 찾기
        item_matches = list(re.finditer(item_pattern, article_text))
        
        if len(item_matches) > 0:
            # 조문 헤더 (첫 번째 항목 전까지)
            first_item_pos = item_matches[0].start()
            article_header = article_text[:first_item_pos].strip()
            
            # 헤더가 있으면 별도 청크로 추가
            if article_header:
                chunks.append({
                    "text": article_header,
                    "metadata": {
                        "chunk_index": len(chunks),
                        "document_id": document.id,
                        "document_type": document.type,
                        "article_number": article_number,
                        "item_number": None,
                        "is_header": True,
                    }
                })
            
            # 항목별로 분할
            for i, match in enumerate(item_matches):
                item_marker = match.group(1)
                
                # 다음 항목까지의 텍스트 추출
                start_pos = match.start()
                if i + 1 < len(item_matches):
                    end_pos = item_matches[i + 1].start()
                else:
                    end_pos = len(article_text)
                
                item_text = article_text[start_pos:end_pos].strip()
                
                if not item_text:
                    continue
                
                # 항목 번호 정규화
                if item_marker.startswith('('):
                    item_num = item_marker.strip('()')
                else:
                    # 원문자 번호를 숫자로 변환
                    item_num = str(ord(item_marker) - ord('①') + 1)
                
                chunks.append({
                    "text": item_text,
                    "metadata": {
                        "chunk_index": len(chunks),
                        "document_id": document.id,
                        "document_type": document.type,
                        "article_number": article_number,
                        "item_number": item_num,
                        "item_marker": item_marker,
                        "is_header": False,
                    }
                })
        else:
            # 항목이 없으면 조문 전체를 하나의 청크로
            chunks.append({
                "text": article_text,
                "metadata": {
                    "chunk_index": 0,
                    "document_id": document.id,
                    "document_type": document.type,
                    "article_number": article_number,
                    "item_number": None,
                    "is_header": False,
                }
            })
        
        return chunks
    
    def _chunk_case(self, document: BaseDocument) -> List[Dict[str, Any]]:
        """
        판례 문서 청킹 (섹션 단위로 분할)
        
        판례 문서는 다음과 같은 섹션으로 구성됩니다:
        - 사건 개요 / 사건의 요지
        - 판결 요지 / 판결 요약
        - 판결 이유 / 판단
        - 참조 조문 / 관련 법령
        """
        chunks = []
        import re
        
        if isinstance(document.content, str):
            content = document.content
            
            # 판례 섹션 패턴
            # 예: "【사건 개요】", "【판결 요지】", "【판결 이유】", "【참조 조문】"
            # 또는 "1. 사건 개요", "2. 판결 요지" 등
            section_patterns = [
                r'【([^】]+)】',  # 【섹션명】
                r'(\d+[\.\s]+[^0-9\n]+?)(?=\d+[\.\s]|【|$)',  # 번호. 섹션명
                r'([가-힣\s]+[:：])(?=\s)',  # 섹션명:
            ]
            
            # 섹션 찾기
            sections = []
            for pattern in section_patterns:
                matches = list(re.finditer(pattern, content))
                if matches:
                    for match in matches:
                        section_title = match.group(1).strip() if match.groups() else match.group(0).strip()
                        start_pos = match.start()
                        sections.append((start_pos, section_title, match))
                    break  # 첫 번째 패턴으로 섹션을 찾으면 중단
            
            if len(sections) > 0:
                # 섹션별로 분할
                for i, (start_pos, section_title, match) in enumerate(sections):
                    # 다음 섹션까지의 텍스트 추출
                    if i + 1 < len(sections):
                        end_pos = sections[i + 1][0]
                    else:
                        end_pos = len(content)
                    
                    section_text = content[start_pos:end_pos].strip()
                    
                    if not section_text:
                        continue
                    
                    # 섹션 타입 분류
                    section_type = self._classify_case_section(section_title)
                    
                    chunks.append({
                        "text": section_text,
                        "metadata": {
                            "chunk_index": len(chunks),
                            "document_id": document.id,
                            "document_type": document.type,
                            "section_title": section_title,
                            "section_type": section_type,
                        }
                    })
            else:
                # 섹션을 찾지 못한 경우 크기 기반 청킹
                # 문장 단위로 분할
                sentences = re.split(r'[。\.]\s+', content)
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
                                    "section_type": "general",
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
                            "section_type": "general",
                        }
                    })
        else:
            chunks = self._chunk_default(document)
        
        return chunks
    
    def _classify_case_section(self, section_title: str) -> str:
        """
        판례 섹션 제목을 분류합니다.
        
        Args:
            section_title: 섹션 제목
            
        Returns:
            섹션 타입 (overview, summary, reasoning, reference, general)
        """
        title_lower = section_title.lower()
        
        # 사건 개요
        if any(keyword in title_lower for keyword in ['사건', '개요', '요지', '사실']):
            return "overview"
        
        # 판결 요지/요약
        if any(keyword in title_lower for keyword in ['판결', '요지', '요약', '결론']):
            return "summary"
        
        # 판결 이유/판단
        if any(keyword in title_lower for keyword in ['이유', '판단', '법리', '법률']):
            return "reasoning"
        
        # 참조 조문/법령
        if any(keyword in title_lower for keyword in ['참조', '조문', '법령', '관련']):
            return "reference"
        
        return "general"
    
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

