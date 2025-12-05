"""배치 처리 파이프라인"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from .converter import JSONConverter
from .cleaner import DataCleaner
from .validator import DocumentValidator

logger = logging.getLogger(__name__)


class BatchProcessor:
    """배치 처리 파이프라인"""
    
    def __init__(self):
        self.converter = JSONConverter()
        self.cleaner = DataCleaner()
        self.validator = DocumentValidator()
    
    def process_file(
        self,
        input_path: Path | str,
        output_path: Path | str,
        doc_type: str,
        clean: bool = True,
        validate: bool = True,
    ) -> tuple[bool, Optional[str]]:
        """
        단일 파일을 처리합니다.
        
        Args:
            input_path: 입력 파일 경로
            output_path: 출력 파일 경로
            doc_type: 문서 타입
            clean: 정제 여부
            validate: 검증 여부
            
        Returns:
            (성공 여부, 오류 메시지 또는 None)
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        try:
            # 1. 원본 데이터 읽기
            with open(input_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            
            # 2. 표준 형식으로 변환
            standard_data = self.converter.convert_to_standard_format(raw_data, doc_type)
            if not standard_data:
                return False, "표준 형식 변환 실패"
            
            # 3. 데이터 정제
            if clean:
                standard_data = self.cleaner.clean(standard_data)
                
                # 필수 필드 검증
                valid, errors = self.cleaner.validate_required_fields(standard_data)
                if not valid:
                    return False, f"필수 필드 검증 실패: {', '.join(errors)}"
            
            # 4. 최종 검증
            if validate:
                success, model = self.validator.validate(standard_data)
                if not success:
                    return False, f"검증 실패: {', '.join(self.validator.get_errors())}"
            
            # 5. 저장
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(standard_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"처리 완료: {input_path.name} -> {output_path.name}")
            return True, None
            
        except Exception as e:
            error_msg = f"파일 처리 중 오류: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def process_directory(
        self,
        input_dir: Path | str,
        output_dir: Path | str,
        doc_type: str,
        pattern: str = "*.json",
        clean: bool = True,
        validate: bool = True,
        remove_duplicates: bool = True,
    ) -> Dict[str, tuple[bool, Optional[str]]]:
        """
        디렉토리 내 모든 파일을 처리합니다.
        
        Args:
            input_dir: 입력 디렉토리
            output_dir: 출력 디렉토리
            doc_type: 문서 타입
            pattern: 파일 패턴 (기본값: *.json)
            clean: 정제 여부
            validate: 검증 여부
            remove_duplicates: 중복 제거 여부
            
        Returns:
            {파일명: (성공 여부, 오류 메시지 또는 None)} 딕셔너리
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        all_data = []
        
        # 모든 파일 처리
        for input_file in input_dir.glob(pattern):
            output_file = output_dir / input_file.name
            success, error = self.process_file(
                input_file, output_file, doc_type, clean, validate
            )
            results[input_file.name] = (success, error)
            
            # 성공한 경우 데이터 수집 (중복 제거용)
            if success and remove_duplicates:
                try:
                    with open(output_file, "r", encoding="utf-8") as f:
                        all_data.append(json.load(f))
                except Exception as e:
                    logger.warning(f"데이터 수집 실패: {output_file.name} - {str(e)}")
        
        # 중복 제거
        if remove_duplicates and all_data:
            unique_data = self.cleaner.remove_duplicates(all_data)
            
            # 중복 제거된 데이터로 다시 저장
            if len(unique_data) < len(all_data):
                logger.info(f"중복 제거: {len(all_data)} -> {len(unique_data)}")
                for data in unique_data:
                    output_file = output_dir / f"{data['id']}.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
        
        return results
    
    def get_statistics(self, results: Dict[str, tuple[bool, Optional[str]]]) -> Dict[str, Any]:
        """
        처리 결과 통계를 반환합니다.
        
        Args:
            results: process_directory 또는 process_file 결과
            
        Returns:
            통계 딕셔너리
        """
        total = len(results)
        success_count = sum(1 for success, _ in results.values() if success)
        failure_count = total - success_count
        
        return {
            "total": total,
            "success": success_count,
            "failure": failure_count,
            "success_rate": success_count / total if total > 0 else 0.0,
        }

