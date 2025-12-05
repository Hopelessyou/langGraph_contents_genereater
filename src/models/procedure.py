"""절차 매뉴얼 데이터 모델"""

from typing import List
from pydantic import BaseModel, Field
from .base import BaseDocument


class ProcedureMetadata(BaseModel):
    """절차 매뉴얼 메타데이터"""
    stage: str = Field(..., description="단계 (예: 경찰조사, 검찰수사, 재판)")
    topic: str = Field(..., description="주제")
    keywords: List[str] = Field(default_factory=list, description="키워드")
    updated_at: str = Field(..., description="최종 수정일")


class ProcedureModel(BaseDocument):
    """절차 매뉴얼 데이터 모델"""
    
    type: str = Field(default="procedure", description="문서 타입")
    content: str = Field(..., description="절차 설명 내용")
    metadata: ProcedureMetadata = Field(..., description="절차 매뉴얼 메타데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "procedure-police-fraud",
                "category": "형사",
                "sub_category": "사기",
                "type": "procedure",
                "title": "사기 사건 경찰 조사 절차",
                "content": "1) 출석 요구 통보 → 2) 피의자 신문조서 작성 → 3) 진술 분석 및 증거 확인 → 4) 검찰 송치.",
                "metadata": {
                    "stage": "경찰조사",
                    "topic": "절차",
                    "keywords": ["경찰 조사", "사기", "절차"],
                    "updated_at": "2024-01-05"
                }
            }
        }

