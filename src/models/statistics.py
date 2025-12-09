"""범죄 통계 데이터 모델"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .base import BaseDocument


class StatisticsMetadata(BaseModel):
    """범죄 통계 메타데이터"""
    
    domain: str = Field(..., description="도메인 (예: crime-statistics)")
    source: str = Field(..., description="데이터 출처")
    date: str = Field(..., description="통계 기준일")
    crime_category_main: str = Field(..., description="범죄 대분류")
    crime_category_mid: Optional[str] = Field(None, description="범죄 중분류")
    crime_category_sub: Optional[str] = Field(None, description="범죄 소분류")
    occurrence: Optional[int] = Field(None, description="발생 건수")
    arrest: Optional[int] = Field(None, description="검거 건수")
    arrest_rate: Optional[float] = Field(None, description="검거율 (%)")
    arrest_male: Optional[int] = Field(None, description="검거인원(남)")
    arrest_female: Optional[int] = Field(None, description="검거인원(여)")
    arrest_unknown: Optional[int] = Field(None, description="검거인원(불상)")
    arrest_corporate: Optional[int] = Field(None, description="검거인원(법인체)")
    tags: List[str] = Field(default_factory=list, description="태그 목록")
    embedding_text: Optional[str] = Field(None, description="임베딩용 텍스트")
    updated_at: str = Field(..., description="최종 수정일")


class StatisticsModel(BaseDocument):
    """범죄 통계 데이터 모델"""
    
    type: str = Field(default="statistics", description="문서 타입")
    content: str = Field(..., description="통계 분석 내용")
    metadata: StatisticsMetadata = Field(..., description="통계 메타데이터")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "crime-지능범죄-사기-사기",
                "category": "형사",
                "sub_category": "지능범죄",
                "type": "statistics",
                "title": "2025년 12월 사기 범죄 통계 분석",
                "content": "2025년 12월 기준 통계 분석에 따르면, '지능범죄-사기-사기' 범죄는 296067건 발생하여 181577건 검거되었으며, 검거율은 약 61.3%이다.",
                "metadata": {
                    "domain": "crime-statistics",
                    "source": "경찰청 전국 범죄 발생 및 검거 현황",
                    "date": "2025-12-31",
                    "crime_category_main": "지능범죄",
                    "crime_category_mid": "사기",
                    "crime_category_sub": "사기",
                    "occurrence": 296067,
                    "arrest": 181577,
                    "arrest_rate": 61.3,
                    "arrest_male": 132019,
                    "arrest_female": 38003,
                    "arrest_unknown": 28380,
                    "arrest_corporate": 282,
                    "tags": ["지능범죄", "사기", "통계", "검거율"],
                    "embedding_text": "사기 발생 296067·검거 181577·검거율 61.3%",
                    "updated_at": "2025-12-31"
                }
            }
        }

