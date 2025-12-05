"""양형기준 요약 데이터 모델"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .base import BaseDocument


class SentencingGuidelineMetadata(BaseModel):
    """양형기준 메타데이터"""
    guideline_type: str = Field(..., description="양형기준 유형")
    factors: List[str] = Field(default_factory=list, description="양형 요소")
    typical_range: Optional[str] = Field(None, description="전형적인 형량 범위")
    updated_at: str = Field(..., description="최종 수정일")


class SentencingGuidelineModel(BaseDocument):
    """양형기준 요약 데이터 모델"""
    
    type: str = Field(default="sentencing_guideline", description="문서 타입")
    content: str = Field(..., description="양형기준 요약 내용")
    metadata: SentencingGuidelineMetadata = Field(..., description="양형기준 메타데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "sentencing-fraud",
                "category": "형사",
                "sub_category": "사기",
                "type": "sentencing_guideline",
                "title": "사기 사건 양형기준 요약",
                "content": "사기 사건의 양형은 피해 규모, 범행 방법, 피해회복 여부 등을 종합적으로 고려합니다.",
                "metadata": {
                    "guideline_type": "형사",
                    "factors": ["피해 규모", "범행 방법", "피해회복 여부", "전과 여부"],
                    "typical_range": "집행유예 ~ 3년 징역",
                    "updated_at": "2024-01-06"
                }
            }
        }

