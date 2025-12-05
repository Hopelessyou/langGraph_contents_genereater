"""스타일 문제 데이터 모델"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .base import BaseDocument


class StyleIssueMetadata(BaseModel):
    """스타일 문제 메타데이터"""
    issue_type: str = Field(..., description="문제 유형 (예: 문법, 용어, 형식)")
    severity: Optional[str] = Field(None, description="심각도 (high, medium, low)")
    examples: List[str] = Field(default_factory=list, description="문제 예시")
    updated_at: str = Field(..., description="최종 수정일")


class StyleIssueModel(BaseDocument):
    """스타일 문제 데이터 모델"""
    
    type: str = Field(default="style_issue", description="문서 타입")
    content: str = Field(..., description="스타일 문제 설명 및 해결 방법")
    metadata: StyleIssueMetadata = Field(..., description="스타일 문제 메타데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "style-issue-legal-term",
                "category": "형사",
                "sub_category": "사기",
                "type": "style_issue",
                "title": "법률 용어 오용 문제",
                "content": "법률 문서 작성 시 '기망'과 '사기'를 구분하여 사용해야 합니다. '기망'은 속이는 행위를 의미하고, '사기'는 그 결과를 의미합니다.",
                "metadata": {
                    "issue_type": "용어",
                    "severity": "high",
                    "examples": ["기망과 사기의 구분", "편취와 횡령의 구분"],
                    "updated_at": "2024-01-09"
                }
            }
        }

