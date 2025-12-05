"""공통 데이터 모델 정의"""

from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field


class BaseDocument(BaseModel):
    """모든 법률 문서의 기본 모델"""
    
    id: str = Field(..., description="문서 고유 식별자")
    category: str = Field(..., description="카테고리 (예: 형사, 민사)")
    sub_category: str = Field(..., description="하위 카테고리 (예: 사기, 계약)")
    type: Literal[
        "statute",
        "case",
        "procedure",
        "manual",
        "case_type",
        "template",
        "sentencing_guideline",
        "faq",
        "keyword_mapping",
        "style_issue",
    ] = Field(..., description="문서 타입")
    title: str = Field(..., description="문서 제목")
    content: str | list[str] = Field(..., description="문서 내용 (문자열 또는 문자열 리스트)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "statute-347",
                "category": "형사",
                "sub_category": "사기",
                "type": "statute",
                "title": "형법 제347조(사기)",
                "content": "① 사람을 기망하여 재물의 교부를 받거나 재산상의 이익을 취득한 자는 10년 이하의 징역 또는 2천만원 이하의 벌금에 처한다.",
                "metadata": {
                    "law_name": "형법",
                    "article_number": "347",
                    "topics": ["사기", "편취"],
                    "source": "법제처",
                    "updated_at": "2024-01-01"
                }
            }
        }

