"""판례 데이터 모델"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .base import BaseDocument


class CaseMetadata(BaseModel):
    """판례 메타데이터"""
    court: str = Field(..., description="법원명 (예: 대법원, 서울중앙지법)")
    year: int = Field(..., description="판결 연도")
    case_number: Optional[str] = Field(None, description="사건 번호")
    keywords: List[str] = Field(default_factory=list, description="키워드")
    holding: str = Field(..., description="판결 요지")
    updated_at: str = Field(..., description="최종 수정일")


class CaseModel(BaseDocument):
    """판례 데이터 모델"""
    
    type: str = Field(default="case", description="문서 타입")
    content: str = Field(..., description="판례 요약 내용")
    metadata: CaseMetadata = Field(..., description="판례 메타데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "case-2023do11234",
                "category": "형사",
                "sub_category": "사기",
                "type": "case",
                "title": "대법원 2023도11234 판결",
                "content": "피고인은 피해자들로부터 투자금을 편취하였고 피해회복이 되지 않아 초범임에도 실형이 선고되었다.",
                "metadata": {
                    "court": "대법원",
                    "year": 2023,
                    "case_number": "2023도11234",
                    "keywords": ["사기", "초범", "실형"],
                    "holding": "초범이라도 피해 규모가 크면 실형 가능",
                    "updated_at": "2024-01-10"
                }
            }
        }

