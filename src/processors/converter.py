"""JSON 변환기 - 원본 데이터를 표준 JSON 형식으로 변환"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from ..models import BaseDocument
from .validator import DocumentValidator

logger = logging.getLogger(__name__)


class JSONConverter:
    """원본 데이터를 표준 JSON 형식으로 변환하는 클래스"""
    
    def __init__(self):
        self.validator = DocumentValidator()
    
    def convert_to_standard_format(
        self,
        raw_data: Dict[str, Any],
        doc_type: str,
    ) -> Optional[Dict[str, Any]]:
        """
        원본 데이터를 표준 JSON 형식으로 변환합니다.
        
        Args:
            raw_data: 원본 데이터 딕셔너리
            doc_type: 문서 타입 (statute, case, procedure 등)
            
        Returns:
            표준 형식의 JSON 딕셔너리 또는 None (변환 실패 시)
        """
        try:
            # 기본 필드 추출
            standard_data = {
                "id": raw_data.get("id", ""),
                "category": raw_data.get("category", ""),
                "sub_category": raw_data.get("sub_category", ""),
                "type": doc_type,
                "title": raw_data.get("title", ""),
                "content": raw_data.get("content", ""),
                "metadata": raw_data.get("metadata", {}),
            }
            
            # 필수 필드 검증
            if not standard_data["id"]:
                logger.warning("id 필드가 없습니다.")
                return None
            
            if not standard_data["title"]:
                logger.warning("title 필드가 없습니다.")
                return None
            
            # 검증
            success, model = self.validator.validate(standard_data)
            if not success:
                logger.error(f"변환된 데이터 검증 실패: {self.validator.get_errors()}")
                return None
            
            return standard_data
            
        except Exception as e:
            logger.error(f"데이터 변환 중 오류 발생: {str(e)}")
            return None
    
    def convert_file(
        self,
        input_path: Path | str,
        output_path: Path | str,
        doc_type: str,
    ) -> bool:
        """
        파일을 읽어서 표준 형식으로 변환하여 저장합니다.
        
        Args:
            input_path: 입력 파일 경로
            output_path: 출력 파일 경로
            doc_type: 문서 타입
            
        Returns:
            성공 여부
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if not input_path.exists():
            logger.error(f"입력 파일이 존재하지 않습니다: {input_path}")
            return False
        
        try:
            # 원본 데이터 읽기
            with open(input_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            
            # 변환
            standard_data = self.convert_to_standard_format(raw_data, doc_type)
            if not standard_data:
                return False
            
            # 출력 디렉토리 생성
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 저장
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(standard_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"변환 완료: {input_path} -> {output_path}")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"파일 변환 중 오류 발생: {str(e)}")
            return False
    
    def convert_batch(
        self,
        input_files: List[Path | str],
        output_dir: Path | str,
        doc_type: str,
    ) -> Dict[str, bool]:
        """
        여러 파일을 일괄 변환합니다.
        
        Args:
            input_files: 입력 파일 경로 리스트
            output_dir: 출력 디렉토리
            doc_type: 문서 타입
            
        Returns:
            {파일명: 성공 여부} 딕셔너리
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        for input_file in input_files:
            input_path = Path(input_file)
            output_path = output_dir / input_path.name
            
            success = self.convert_file(input_path, output_path, doc_type)
            results[input_path.name] = success
        
        return results

