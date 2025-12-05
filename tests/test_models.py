"""데이터 모델 단위 테스트"""

import pytest
from datetime import datetime

from src.models import (
    StatuteModel,
    CaseModel,
    ProcedureModel,
    TemplateModel,
    ManualModel,
    CaseTypeModel,
    SentencingGuidelineModel,
    FAQModel,
    KeywordMappingModel,
    StyleIssueModel,
)


class TestStatuteModel:
    """법령 모델 테스트"""
    
    def test_statute_model_creation(self):
        """법령 모델 생성 테스트"""
        statute = StatuteModel(
            id="statute-test-1",
            category="형사",
            sub_category="사기",
            type="statute",
            title="형법 제347조(사기)",
            content="사기 조문 내용",
            metadata={
                "law_name": "형법",
                "article_number": "347",
                "topics": ["사기"],
                "source": "법제처",
                "updated_at": "2024-01-01",
            },
        )
        
        assert statute.id == "statute-test-1"
        assert statute.type == "statute"
        assert statute.metadata.law_name == "형법"
        assert statute.metadata.article_number == "347"
    
    def test_statute_model_validation(self):
        """법령 모델 검증 테스트"""
        # 필수 필드 누락 시 오류
        with pytest.raises(Exception):
            StatuteModel(
                id="test",
                category="형사",
                sub_category="사기",
                type="statute",
                title="",
                content="",
                metadata={},
            )


class TestCaseModel:
    """판례 모델 테스트"""
    
    def test_case_model_creation(self):
        """판례 모델 생성 테스트"""
        case = CaseModel(
            id="case-test-1",
            category="형사",
            sub_category="사기",
            type="case",
            title="대법원 2024도1 판결",
            content="판례 내용",
            metadata={
                "court": "대법원",
                "year": 2024,
                "case_number": "2024도1",
                "keywords": ["사기"],
                "holding": "판결 요지",
                "updated_at": "2024-01-01",
            },
        )
        
        assert case.id == "case-test-1"
        assert case.type == "case"
        assert case.metadata.court == "대법원"
        assert case.metadata.year == 2024


class TestTemplateModel:
    """템플릿 모델 테스트"""
    
    def test_template_model_creation(self):
        """템플릿 모델 생성 테스트"""
        template = TemplateModel(
            id="template-test-1",
            category="형사",
            sub_category="사기",
            type="template",
            title="템플릿 제목",
            content=["항목 1", "항목 2", "항목 3"],
            metadata={
                "usage": "콘텐츠 생성",
                "output_styles": ["블로그형"],
                "updated_at": "2024-01-01",
            },
        )
        
        assert template.id == "template-test-1"
        assert isinstance(template.content, list)
        assert len(template.content) == 3


class TestFAQModel:
    """FAQ 모델 테스트"""
    
    def test_faq_model_creation(self):
        """FAQ 모델 생성 테스트"""
        faq = FAQModel(
            id="faq-test-1",
            category="형사",
            sub_category="사기",
            type="faq",
            title="FAQ 제목",
            question="질문 내용",
            content="답변 내용",
            metadata={
                "question_type": "처벌",
                "related_topics": ["초범"],
                "updated_at": "2024-01-01",
            },
        )
        
        assert faq.id == "faq-test-1"
        assert faq.question == "질문 내용"
        assert faq.content == "답변 내용"

