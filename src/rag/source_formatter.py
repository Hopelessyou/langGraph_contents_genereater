"""검색 결과 출처 표시"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SourceFormatter:
    """출처 포맷터"""
    
    @staticmethod
    def format_source(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        검색 결과에서 출처 정보를 포맷팅합니다.
        
        Args:
            result: 검색 결과 딕셔너리
            
        Returns:
            포맷팅된 출처 정보
        """
        metadata = result.get("metadata", {})
        doc_type = metadata.get("type", "")
        
        source_info = {
            "id": result.get("id", ""),
            "type": doc_type,
            "title": metadata.get("title", ""),
        }
        
        # 타입별 출처 정보 추가
        if doc_type == "statute":
            source_info["law_name"] = metadata.get("law_name", "")
            source_info["article_number"] = metadata.get("article_number", "")
            source_info["citation"] = f"{metadata.get('law_name', '')} 제{metadata.get('article_number', '')}조"
        
        elif doc_type == "case":
            source_info["court"] = metadata.get("court", "")
            source_info["year"] = metadata.get("year", "")
            source_info["case_number"] = metadata.get("case_number", "")
            source_info["citation"] = (
                f"{metadata.get('court', '')} "
                f"{metadata.get('year', '')}년 "
                f"{metadata.get('case_number', '')}"
            )
        
        elif doc_type == "procedure":
            source_info["stage"] = metadata.get("stage", "")
            source_info["citation"] = f"절차 매뉴얼 - {metadata.get('stage', '')}"
        
        else:
            source_info["citation"] = metadata.get("title", "")
        
        return source_info
    
    @staticmethod
    def format_sources(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        여러 검색 결과의 출처를 포맷팅합니다.
        
        Args:
            results: 검색 결과 리스트
            
        Returns:
            포맷팅된 출처 리스트
        """
        return [SourceFormatter.format_source(r) for r in results]
    
    @staticmethod
    def format_citation_text(sources: List[Dict[str, Any]]) -> str:
        """
        출처를 텍스트 형식으로 포맷팅합니다.
        
        Args:
            sources: 출처 리스트
            
        Returns:
            포맷팅된 출처 텍스트
        """
        if not sources:
            return ""
        
        citation_parts = ["\n[출처]"]
        for i, source in enumerate(sources, 1):
            citation = source.get("citation", source.get("title", ""))
            citation_parts.append(f"{i}. {citation}")
        
        return "\n".join(citation_parts)

