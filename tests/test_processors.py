"""데이터 처리 파이프라인 단위 테스트"""

import pytest
import json
from pathlib import Path
import tempfile

from src.processors import (
    DocumentValidator,
    JSONConverter,
    DataCleaner,
    BatchProcessor,
    QualityChecker,
)
from src.models import StatuteModel


class TestDocumentValidator:
    """문서 검증기 테스트"""
    
    def test_validate_statute(self):
        """법령 문서 검증 테스트"""
        validator = DocumentValidator()
        
        data = {
            "id": "statute-test",
            "category": "형사",
            "sub_category": "사기",
            "type": "statute",
            "title": "형법 제347조",
            "content": "조문 내용",
            "metadata": {
                "law_name": "형법",
                "article_number": "347",
                "topics": ["사기"],
                "source": "법제처",
                "updated_at": "2024-01-01",
            },
        }
        
        success, model = validator.validate(data)
        assert success is True
        assert isinstance(model, StatuteModel)
    
    def test_validate_invalid_data(self):
        """잘못된 데이터 검증 테스트"""
        validator = DocumentValidator()
        
        data = {
            "id": "test",
            # 필수 필드 누락
        }
        
        success, model = validator.validate(data)
        assert success is False
        assert model is None
        assert len(validator.get_errors()) > 0


class TestDataCleaner:
    """데이터 정제기 테스트"""
    
    def test_clean_whitespace(self):
        """공백 정제 테스트"""
        cleaner = DataCleaner()
        
        data = {
            "title": "  제목  ",
            "content": "  내용  ",
        }
        
        cleaned = cleaner.clean(data, rules=["whitespace"])
        assert cleaned["title"] == "제목"
        assert cleaned["content"] == "내용"
    
    def test_remove_duplicates(self):
        """중복 제거 테스트"""
        cleaner = DataCleaner()
        
        data_list = [
            {"id": "1", "title": "문서 1"},
            {"id": "2", "title": "문서 2"},
            {"id": "1", "title": "문서 1"},  # 중복
        ]
        
        unique = cleaner.remove_duplicates(data_list, key_field="id")
        assert len(unique) == 2
        assert unique[0]["id"] == "1"
        assert unique[1]["id"] == "2"


class TestJSONConverter:
    """JSON 변환기 테스트"""
    
    def test_convert_to_standard_format(self):
        """표준 형식 변환 테스트"""
        converter = JSONConverter()
        
        raw_data = {
            "id": "test-1",
            "title": "테스트 제목",
            "content": "테스트 내용",
            "category": "형사",
            "sub_category": "사기",
            "metadata": {
                "law_name": "형법",
                "article_number": "347",
                "updated_at": "2024-01-01",
            },
        }
        
        standard = converter.convert_to_standard_format(raw_data, "statute")
        assert standard is not None
        assert standard["id"] == "test-1"
        assert standard["type"] == "statute"


class TestQualityChecker:
    """품질 검증기 테스트"""
    
    def test_check_quality(self):
        """품질 검사 테스트"""
        checker = QualityChecker()
        
        data = {
            "id": "test-1",
            "type": "statute",
            "title": "테스트 제목",
            "content": "충분히 긴 내용입니다. 최소 10자 이상이어야 합니다.",
            "category": "형사",
            "sub_category": "사기",
            "metadata": {
                "law_name": "형법",
                "article_number": "347",
                "updated_at": "2024-01-01",
            },
        }
        
        result = checker.check_quality(data)
        assert "valid" in result
        assert "score" in result

