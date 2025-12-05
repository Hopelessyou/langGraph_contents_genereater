"""JSON 스키마 검증기"""

import json
from typing import Any, Dict, List, Optional
from pathlib import Path

from ..models import (
    BaseDocument,
    StatuteModel,
    CaseModel,
    ProcedureModel,
    TemplateModel,
    ManualModel,
    CaseTypeModel,
    SentencingGuidelineModel,
    FAQModel,
    KeywordMappingModel,
    StyleIssueModel,
)


class DocumentValidator:
    """문서 검증기"""
    
    # 타입별 모델 매핑
    TYPE_MODEL_MAP = {
        "statute": StatuteModel,
        "case": CaseModel,
        "procedure": ProcedureModel,
        "template": TemplateModel,
        "manual": ManualModel,
        "case_type": CaseTypeModel,
        "sentencing_guideline": SentencingGuidelineModel,
        "faq": FAQModel,
        "keyword_mapping": KeywordMappingModel,
        "style_issue": StyleIssueModel,
    }
    
    def __init__(self):
        self.errors: List[str] = []
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, Optional[BaseDocument]]:
        """
        JSON 데이터를 검증하고 모델 인스턴스를 반환합니다.
        
        Args:
            data: 검증할 JSON 데이터 딕셔너리
            
        Returns:
            (성공 여부, 모델 인스턴스 또는 None)
        """
        self.errors.clear()
        
        # 기본 필드 검증
        if not isinstance(data, dict):
            self.errors.append("데이터가 딕셔너리 형식이 아닙니다.")
            return False, None
        
        # type 필드 확인
        doc_type = data.get("type")
        if not doc_type:
            self.errors.append("'type' 필드가 없습니다.")
            return False, None
        
        if doc_type not in self.TYPE_MODEL_MAP:
            self.errors.append(f"지원하지 않는 문서 타입: {doc_type}")
            return False, None
        
        # 해당 타입의 모델로 검증
        model_class = self.TYPE_MODEL_MAP[doc_type]
        
        try:
            model = model_class(**data)
            return True, model
        except Exception as e:
            self.errors.append(f"검증 실패: {str(e)}")
            return False, None
    
    def validate_file(self, file_path: Path | str) -> tuple[bool, Optional[BaseDocument]]:
        """
        JSON 파일을 검증합니다.
        
        Args:
            file_path: JSON 파일 경로
            
        Returns:
            (성공 여부, 모델 인스턴스 또는 None)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.errors.append(f"파일이 존재하지 않습니다: {file_path}")
            return False, None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return self.validate(data)
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON 파싱 오류: {str(e)}")
            return False, None
        except Exception as e:
            self.errors.append(f"파일 읽기 오류: {str(e)}")
            return False, None
    
    def validate_batch(self, data_list: List[Dict[str, Any]]) -> Dict[str, tuple[bool, Optional[BaseDocument]]]:
        """
        여러 문서를 일괄 검증합니다.
        
        Args:
            data_list: 검증할 JSON 데이터 리스트
            
        Returns:
            {문서 ID: (성공 여부, 모델 인스턴스 또는 None)} 딕셔너리
        """
        results = {}
        
        for data in data_list:
            doc_id = data.get("id", "unknown")
            success, model = self.validate(data)
            results[doc_id] = (success, model)
        
        return results
    
    def get_errors(self) -> List[str]:
        """검증 오류 목록을 반환합니다."""
        return self.errors.copy()


def validate_document(data: Dict[str, Any]) -> tuple[bool, Optional[BaseDocument], List[str]]:
    """
    문서를 검증하는 편의 함수.
    
    Args:
        data: 검증할 JSON 데이터
        
    Returns:
        (성공 여부, 모델 인스턴스 또는 None, 오류 목록)
    """
    validator = DocumentValidator()
    success, model = validator.validate(data)
    return success, model, validator.get_errors()

