"""사건 유형 정의서 데이터 모델"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .base import BaseDocument


class CaseTypeMetadata(BaseModel):
    """사건 유형 메타데이터"""
    case_type_code: Optional[str] = Field(None, description="사건 유형 코드")
    related_keywords: List[str] = Field(default_factory=list, description="관련 키워드")
    typical_penalty: Optional[str] = Field(None, description="전형적인 처벌")
    updated_at: str = Field(..., description="최종 수정일")


class CaseTypeModel(BaseDocument):
    """사건 유형 정의서 데이터 모델"""
    
    type: str = Field(default="case_type", description="문서 타입")
    content: str = Field(..., description="사건 유형 정의 내용")
    metadata: CaseTypeMetadata = Field(..., description="사건 유형 메타데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "case-type-fraud",
                "category": "형사",
                "sub_category": "사기",
                "type": "case_type",
                "title": "사기 사건 유형 정의",
                "content": "사기 사건은 사람을 기망하여 재물의 교부를 받거나 재산상의 이익을 취득하는 범죄입니다.",
                "metadata": {
                    "case_type_code": "FRAUD",
                    "related_keywords": ["사기", "편취", "기망"],
                    "typical_penalty": "10년 이하 징역 또는 2천만원 이하 벌금",
                    "updated_at": "2024-01-04"
                }
            }
        }

