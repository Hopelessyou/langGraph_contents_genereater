"""법률 FAQ 데이터 모델"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .base import BaseDocument


class FAQMetadata(BaseModel):
    """FAQ 메타데이터"""
    question_type: Optional[str] = Field(None, description="질문 유형")
    related_topics: List[str] = Field(default_factory=list, description="관련 주제")
    frequency: Optional[int] = Field(None, description="질문 빈도")
    updated_at: str = Field(..., description="최종 수정일")


class FAQModel(BaseDocument):
    """법률 FAQ 데이터 모델"""
    
    type: str = Field(default="faq", description="문서 타입")
    content: str = Field(..., description="FAQ 답변 내용")
    metadata: FAQMetadata = Field(..., description="FAQ 메타데이터")
    question: str = Field(..., description="질문 내용")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "faq-fraud-first-time",
                "category": "형사",
                "sub_category": "사기",
                "type": "faq",
                "title": "사기 초범은 집행유예가 가능한가요?",
                "question": "사기 초범은 집행유예가 가능한가요?",
                "content": "사기 초범이라도 피해 규모가 크거나 피해회복이 되지 않으면 실형이 선고될 수 있습니다. 다만, 피해회복을 하고 반성하는 태도를 보이면 집행유예 가능성이 높아집니다.",
                "metadata": {
                    "question_type": "처벌",
                    "related_topics": ["초범", "집행유예", "실형"],
                    "frequency": 100,
                    "updated_at": "2024-01-07"
                }
            }
        }

