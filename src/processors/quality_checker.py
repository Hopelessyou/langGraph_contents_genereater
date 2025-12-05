"""데이터 품질 검증 도구"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import logging

from ..models import BaseDocument
from .validator import DocumentValidator
from .cleaner import DataCleaner

logger = logging.getLogger(__name__)


class QualityChecker:
    """데이터 품질 검증 도구"""
    
    def __init__(self):
        self.validator = DocumentValidator()
        self.cleaner = DataCleaner()
    
    def check_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        데이터 품질을 검사합니다.
        
        Args:
            data: 검사할 데이터
            
        Returns:
            품질 검사 결과 딕셔너리
        """
        results = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "score": 0.0,
            "checks": {},
        }
        
        # 1. 스키마 검증
        success, model = self.validator.validate(data)
        results["checks"]["schema_validation"] = success
        if not success:
            results["errors"].extend(self.validator.get_errors())
        else:
            results["score"] += 30.0
        
        # 2. 필수 필드 검증
        valid, errors = self.cleaner.validate_required_fields(data)
        results["checks"]["required_fields"] = valid
        if not valid:
            results["errors"].extend(errors)
        else:
            results["score"] += 20.0
        
        # 3. 내용 품질 검사
        content_quality = self._check_content_quality(data)
        results["checks"]["content_quality"] = content_quality
        results["score"] += content_quality["score"]
        
        if content_quality["warnings"]:
            results["warnings"].extend(content_quality["warnings"])
        
        # 4. 메타데이터 품질 검사
        metadata_quality = self._check_metadata_quality(data)
        results["checks"]["metadata_quality"] = metadata_quality
        results["score"] += metadata_quality["score"]
        
        if metadata_quality["warnings"]:
            results["warnings"].extend(metadata_quality["warnings"])
        
        # 최종 검증
        results["valid"] = (
            results["checks"]["schema_validation"]
            and results["checks"]["required_fields"]
            and results["score"] >= 70.0
        )
        
        return results
    
    def _check_content_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """내용 품질 검사"""
        quality = {
            "score": 0.0,
            "warnings": [],
        }
        
        title = data.get("title", "")
        content = data.get("content", "")
        
        # 제목 길이 검사
        if len(title) < 5:
            quality["warnings"].append("제목이 너무 짧습니다 (5자 미만)")
        elif len(title) > 200:
            quality["warnings"].append("제목이 너무 깁니다 (200자 초과)")
        else:
            quality["score"] += 15.0
        
        # 내용 길이 검사
        if isinstance(content, str):
            content_length = len(content)
        elif isinstance(content, list):
            content_length = sum(len(str(item)) for item in content)
        else:
            content_length = 0
        
        if content_length < 10:
            quality["warnings"].append("내용이 너무 짧습니다 (10자 미만)")
        elif content_length > 50000:
            quality["warnings"].append("내용이 너무 깁니다 (50,000자 초과)")
        else:
            quality["score"] += 15.0
        
        # 빈 필드 검사
        if not title.strip():
            quality["warnings"].append("제목이 비어있습니다")
        else:
            quality["score"] += 5.0
        
        if not content or (isinstance(content, str) and not content.strip()):
            quality["warnings"].append("내용이 비어있습니다")
        else:
            quality["score"] += 5.0
        
        return quality
    
    def _check_metadata_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """메타데이터 품질 검사"""
        quality = {
            "score": 0.0,
            "warnings": [],
        }
        
        metadata = data.get("metadata", {})
        
        # 메타데이터 존재 여부
        if not metadata:
            quality["warnings"].append("메타데이터가 없습니다")
        else:
            quality["score"] += 10.0
        
        # updated_at 필드 검사
        if "updated_at" in metadata:
            quality["score"] += 5.0
        else:
            quality["warnings"].append("updated_at 필드가 없습니다")
        
        # 타입별 특정 메타데이터 검사
        doc_type = data.get("type", "")
        
        if doc_type == "statute":
            if "law_name" in metadata and "article_number" in metadata:
                quality["score"] += 5.0
            else:
                quality["warnings"].append("법령 메타데이터가 불완전합니다")
        
        elif doc_type == "case":
            if "court" in metadata and "year" in metadata:
                quality["score"] += 5.0
            else:
                quality["warnings"].append("판례 메타데이터가 불완전합니다")
        
        return quality
    
    def check_batch(
        self,
        data_list: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        여러 데이터의 품질을 일괄 검사합니다.
        
        Args:
            data_list: 검사할 데이터 리스트
            
        Returns:
            일괄 검사 결과
        """
        results = {
            "total": len(data_list),
            "valid_count": 0,
            "invalid_count": 0,
            "average_score": 0.0,
            "details": [],
        }
        
        total_score = 0.0
        
        for data in data_list:
            quality_result = self.check_quality(data)
            results["details"].append({
                "id": data.get("id", "unknown"),
                "quality": quality_result,
            })
            
            if quality_result["valid"]:
                results["valid_count"] += 1
            else:
                results["invalid_count"] += 1
            
            total_score += quality_result["score"]
        
        if results["total"] > 0:
            results["average_score"] = total_score / results["total"]
        
        return results
    
    def check_file(self, file_path: Path | str) -> Dict[str, Any]:
        """
        파일의 품질을 검사합니다.
        
        Args:
            file_path: 검사할 파일 경로
            
        Returns:
            품질 검사 결과
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                "valid": False,
                "errors": [f"파일이 존재하지 않습니다: {file_path}"],
            }
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return self.check_quality(data)
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"파일 읽기 오류: {str(e)}"],
            }

