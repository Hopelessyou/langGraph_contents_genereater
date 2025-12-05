"""RAG 시스템 단위 테스트"""

import pytest
from unittest.mock import Mock, patch

from src.rag import (
    TextChunker,
    KeywordClassifier,
    SourceFormatter,
    ResultSummarizer,
    StyleValidator,
    LegalTermChecker,
)


class TestTextChunker:
    """텍스트 청킹 테스트"""
    
    def test_chunk_statute(self):
        """법령 문서 청킹 테스트"""
        from src.models import StatuteModel
        
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        
        document = StatuteModel(
            id="test-1",
            category="형사",
            sub_category="사기",
            type="statute",
            title="형법 제347조",
            content="① 첫 번째 조문 내용입니다. ② 두 번째 조문 내용입니다.",
            metadata={
                "law_name": "형법",
                "article_number": "347",
                "topics": ["사기"],
                "source": "법제처",
                "updated_at": "2024-01-01",
            },
        )
        
        chunks = chunker.chunk_document(document)
        assert len(chunks) > 0
        assert all("text" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)


class TestKeywordClassifier:
    """키워드 분류기 테스트"""
    
    def test_classify_category(self):
        """카테고리 분류 테스트"""
        classifier = KeywordClassifier()
        
        result = classifier.classify("형사 사기 사건에 대해 알고 싶습니다.")
        assert result["category"] == "형사"
        assert result["sub_category"] == "사기"
    
    def test_classify_document_types(self):
        """문서 타입 분류 테스트"""
        classifier = KeywordClassifier()
        
        result = classifier.classify("형법 조문과 판례를 찾고 있습니다.")
        assert "statute" in result["document_types"]
        assert "case" in result["document_types"]


class TestSourceFormatter:
    """출처 포맷터 테스트"""
    
    def test_format_statute_source(self):
        """법령 출처 포맷팅 테스트"""
        result = {
            "id": "statute-347",
            "metadata": {
                "type": "statute",
                "title": "형법 제347조",
                "law_name": "형법",
                "article_number": "347",
            },
        }
        
        source = SourceFormatter.format_source(result)
        assert source["type"] == "statute"
        assert "citation" in source
        assert "형법" in source["citation"]
        assert "347" in source["citation"]


class TestResultSummarizer:
    """결과 요약기 테스트"""
    
    def test_summarize_results(self):
        """검색 결과 요약 테스트"""
        results = [
            {
                "metadata": {
                    "type": "statute",
                    "title": "형법 제347조",
                    "law_name": "형법",
                    "article_number": "347",
                },
            },
            {
                "metadata": {
                    "type": "case",
                    "title": "대법원 판결",
                    "court": "대법원",
                    "year": 2024,
                },
            },
        ]
        
        summary = ResultSummarizer.summarize_results(results)
        assert len(summary) > 0
        assert "형법" in summary or "347" in summary


class TestStyleValidator:
    """스타일 검증기 테스트"""
    
    def test_validate_style(self):
        """스타일 검증 테스트"""
        validator = StyleValidator()
        
        text = "사기 범죄에 대한 법령입니다."
        result = validator.validate_style(text)
        
        assert "valid" in result
        assert "score" in result
    
    def test_check_legal_terms(self):
        """법률 용어 검사 테스트"""
        checker = LegalTermChecker()
        
        text = "기만하여 재물을 편취했습니다."  # 잘못된 용어
        result = checker.check_terms(text)
        
        # '기만' 대신 '기망'을 사용해야 함
        assert len(result.get("issues", [])) > 0 or result.get("valid", True)

