"""템플릿 데이터 모델"""

from typing import List
from pydantic import BaseModel, Field
from .base import BaseDocument


class TemplateMetadata(BaseModel):
    """템플릿 메타데이터"""
    usage: str = Field(..., description="사용 용도")
    output_styles: List[str] = Field(default_factory=list, description="출력 스타일 (예: 블로그형, 뉴스형, 네이버형)")
    updated_at: str = Field(..., description="최종 수정일")


class TemplateModel(BaseDocument):
    """템플릿 데이터 모델"""
    
    type: str = Field(default="template", description="문서 타입")
    content: List[str] = Field(..., description="템플릿 구조 (문자열 리스트)")
    metadata: TemplateMetadata = Field(..., description="템플릿 메타데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "template-criminal-fraud",
                "category": "형사",
                "sub_category": "사기",
                "type": "template",
                "title": "형사사기 콘텐츠 템플릿",
                "content": [
                    "1. 사건 요약",
                    "2. 사기 초범의 흔한 오해",
                    "3. 관련 법령 설명",
                    "4. 최신 판례 경향",
                    "5. 초범 선처 요건",
                    "6. 경찰 조사 포인트",
                    "7. 결론 및 조언"
                ],
                "metadata": {
                    "usage": "콘텐츠 생성 템플릿",
                    "output_styles": ["블로그형", "뉴스형", "네이버형"],
                    "updated_at": "2024-01-02"
                }
            }
        }

