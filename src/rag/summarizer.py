"""검색 결과 요약 기능"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ResultSummarizer:
    """검색 결과 요약기"""
    
    @staticmethod
    def summarize_results(
        results: List[Dict[str, Any]],
        max_length: int = 500,
    ) -> str:
        """
        검색 결과를 요약합니다.
        
        Args:
            results: 검색 결과 리스트
            max_length: 최대 요약 길이
            
        Returns:
            요약 텍스트
        """
        if not results:
            return "검색 결과가 없습니다."
        
        summary_parts = []
        
        # 각 결과의 핵심 정보 추출
        for i, result in enumerate(results[:3], 1):  # 상위 3개만
            metadata = result.get("metadata", {})
            doc_type = metadata.get("type", "")
            title = metadata.get("title", "")
            
            # 타입별 요약
            if doc_type == "statute":
                summary_parts.append(
                    f"{i}. {title} - "
                    f"{metadata.get('law_name', '')} 제{metadata.get('article_number', '')}조"
                )
            elif doc_type == "case":
                summary_parts.append(
                    f"{i}. {title} - "
                    f"{metadata.get('court', '')} {metadata.get('year', '')}년 판결"
                )
            else:
                summary_parts.append(f"{i}. {title}")
        
        summary = "\n".join(summary_parts)
        
        # 길이 제한
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    @staticmethod
    def summarize_by_type(
        results: List[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        타입별로 검색 결과를 그룹화합니다.
        
        Args:
            results: 검색 결과 리스트
            
        Returns:
            타입별로 그룹화된 결과
        """
        grouped = {}
        
        for result in results:
            doc_type = result.get("metadata", {}).get("type", "unknown")
            if doc_type not in grouped:
                grouped[doc_type] = []
            grouped[doc_type].append(result)
        
        return grouped

