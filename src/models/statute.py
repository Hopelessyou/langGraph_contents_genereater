"""법령 데이터 모델"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseDocument


class StatuteMetadata(BaseModel):
    """법령 메타데이터"""
    law_name: str = Field(..., description="법령명 (예: 형법)")
    article_number: str = Field(..., description="조문 번호")
    topics: List[str] = Field(default_factory=list, description="관련 주제 키워드")
    source: str = Field(default="법제처", description="출처")
    updated_at: str = Field(..., description="최종 수정일")


class StatuteModel(BaseDocument):
    """법령 데이터 모델"""
    
    type: str = Field(default="statute", description="문서 타입")
    content: str = Field(..., description="법령 조문 내용")
    metadata: StatuteMetadata = Field(..., description="법령 메타데이터")

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

