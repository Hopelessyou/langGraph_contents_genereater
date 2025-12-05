"""데이터 정제 및 검증 로직"""

import re
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """데이터 정제 클래스"""
    
    def __init__(self):
        self.cleaning_rules = {
            "whitespace": self._clean_whitespace,
            "special_chars": self._clean_special_chars,
            "empty_fields": self._remove_empty_fields,
            "normalize_text": self._normalize_text,
        }
    
    def clean(self, data: Dict[str, Any], rules: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        데이터를 정제합니다.
        
        Args:
            data: 정제할 데이터 딕셔너리
            rules: 적용할 정제 규칙 리스트 (None이면 모든 규칙 적용)
            
        Returns:
            정제된 데이터 딕셔너리
        """
        cleaned_data = data.copy()
        
        if rules is None:
            rules = list(self.cleaning_rules.keys())
        
        for rule in rules:
            if rule in self.cleaning_rules:
                cleaned_data = self.cleaning_rules[rule](cleaned_data)
        
        return cleaned_data
    
    def _clean_whitespace(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """공백 정제"""
        cleaned = data.copy()
        
        # 문자열 필드의 앞뒤 공백 제거
        for key, value in cleaned.items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
            elif isinstance(value, dict):
                cleaned[key] = self._clean_whitespace(value)
            elif isinstance(value, list):
                cleaned[key] = [
                    item.strip() if isinstance(item, str) else item
                    for item in value
                ]
        
        return cleaned
    
    def _clean_special_chars(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """특수 문자 정제"""
        cleaned = data.copy()
        
        # 제목과 내용에서 불필요한 특수 문자 제거
        for field in ["title", "content"]:
            if field in cleaned and isinstance(cleaned[field], str):
                # 연속된 공백을 하나로
                cleaned[field] = re.sub(r'\s+', ' ', cleaned[field])
                # 제어 문자 제거
                cleaned[field] = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned[field])
        
        return cleaned
    
    def _remove_empty_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """빈 필드 제거 (선택적)"""
        cleaned = {}
        
        for key, value in data.items():
            # 빈 문자열, None, 빈 리스트, 빈 딕셔너리는 제거하지 않음 (메타데이터 구조 유지)
            if value is not None:
                cleaned[key] = value
        
        return cleaned
    
    def _normalize_text(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """텍스트 정규화"""
        cleaned = data.copy()
        
        # 한글 자모 정규화
        for field in ["title", "content"]:
            if field in cleaned and isinstance(cleaned[field], str):
                # 전각 문자를 반각으로 (일부)
                cleaned[field] = cleaned[field].replace("（", "(").replace("）", ")")
                cleaned[field] = cleaned[field].replace("：", ":").replace("，", ",")
        
        return cleaned
    
    def validate_required_fields(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        필수 필드 검증
        
        Args:
            data: 검증할 데이터
            
        Returns:
            (성공 여부, 오류 메시지 리스트)
        """
        errors = []
        required_fields = ["id", "type", "title", "content"]
        
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"필수 필드 '{field}'가 없거나 비어있습니다.")
        
        return len(errors) == 0, errors
    
    def remove_duplicates(
        self,
        data_list: List[Dict[str, Any]],
        key_field: str = "id"
    ) -> List[Dict[str, Any]]:
        """
        중복 데이터 제거
        
        Args:
            data_list: 데이터 리스트
            key_field: 중복 판단 기준 필드 (기본값: id)
            
        Returns:
            중복 제거된 데이터 리스트
        """
        seen = set()
        unique_data = []
        
        for item in data_list:
            key_value = item.get(key_field)
            if key_value and key_value not in seen:
                seen.add(key_value)
                unique_data.append(item)
            elif not key_value:
                logger.warning(f"중복 제거 기준 필드 '{key_field}'가 없습니다.")
        
        removed_count = len(data_list) - len(unique_data)
        if removed_count > 0:
            logger.info(f"중복 데이터 {removed_count}건 제거됨")
        
        return unique_data

