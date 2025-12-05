"""실무 매뉴얼 데이터 모델"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .base import BaseDocument


class ManualMetadata(BaseModel):
    """실무 매뉴얼 메타데이터"""
    manual_type: str = Field(..., description="매뉴얼 유형")
    target_audience: Optional[str] = Field(None, description="대상 독자")
    keywords: List[str] = Field(default_factory=list, description="키워드")
    updated_at: str = Field(..., description="최종 수정일")


class ManualModel(BaseDocument):
    """실무 매뉴얼 데이터 모델"""
    
    type: str = Field(default="manual", description="문서 타입")
    content: str = Field(..., description="실무 매뉴얼 내용")
    metadata: ManualMetadata = Field(..., description="실무 매뉴얼 메타데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "manual-fraud-defense",
                "category": "형사",
                "sub_category": "사기",
                "type": "manual",
                "title": "사기 사건 변호 실무 매뉴얼",
                "content": "사기 사건에서 변호사가 주의해야 할 실무 포인트와 대응 전략을 설명합니다.",
                "metadata": {
                    "manual_type": "변호 실무",
                    "target_audience": "변호사",
                    "keywords": ["사기", "변호", "실무"],
                    "updated_at": "2024-01-03"
                }
            }
        }

