"""키워드-사건 맵핑 데이터 모델"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from .base import BaseDocument


class KeywordMappingMetadata(BaseModel):
    """키워드 맵핑 메타데이터"""
    keywords: List[str] = Field(..., description="키워드 리스트")
    mapped_case_types: List[str] = Field(default_factory=list, description="맵핑된 사건 유형")
    confidence: Optional[float] = Field(None, description="맵핑 신뢰도 (0.0-1.0)")
    updated_at: str = Field(..., description="최종 수정일")


class KeywordMappingModel(BaseDocument):
    """키워드-사건 맵핑 데이터 모델"""
    
    type: str = Field(default="keyword_mapping", description="문서 타입")
    content: Dict[str, List[str]] = Field(..., description="키워드-사건 유형 맵핑 딕셔너리")
    metadata: KeywordMappingMetadata = Field(..., description="키워드 맵핑 메타데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "keyword-mapping-fraud",
                "category": "형사",
                "sub_category": "사기",
                "type": "keyword_mapping",
                "title": "사기 관련 키워드 맵핑",
                "content": {
                    "투자금 편취": ["사기", "특정경제범죄가중처벌법"],
                    "피싱": ["사기", "정보통신망법"],
                    "보이스피싱": ["사기", "정보통신망법"]
                },
                "metadata": {
                    "keywords": ["투자금 편취", "피싱", "보이스피싱"],
                    "mapped_case_types": ["사기", "특정경제범죄가중처벌법", "정보통신망법"],
                    "confidence": 0.95,
                    "updated_at": "2024-01-08"
                }
            }
        }

