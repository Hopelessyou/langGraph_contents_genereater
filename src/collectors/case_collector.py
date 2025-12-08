"""판례 데이터 수집 스크립트"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests

from ..models import CaseModel

logger = logging.getLogger(__name__)


class CaseCollector:
    """판례 데이터 수집기"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("data/collected/cases")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_from_api(
        self,
        court: str = "대법원",
        year: Optional[int] = None,
        case_number: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        법원 판례 시스템에서 판례 데이터를 수집합니다.
        
        Args:
            court: 법원명 (대법원, 고등법원 등)
            year: 연도
            case_number: 사건 번호
            keywords: 검색 키워드
            
        Returns:
            수집된 데이터 딕셔너리
        """
        try:
            # 법원 판례 시스템 API (예시)
            # 실제 구현 시 법원 판례 시스템 API 문서 참고 필요
            
            # ID 생성: 키워드가 있으면 키워드를 포함하여 고유 ID 생성
            if keywords and len(keywords) > 0:
                keyword_str = "-".join(keywords[:2])  # 최대 2개 키워드만 사용
                case_id = f"case-{court}-{keyword_str}-{year or 'unknown'}-{case_number or 'unknown'}"
                title = f"{court} {keywords[0]} 관련 판결"
            else:
                case_id = f"case-{court}-{year or 'unknown'}-{case_number or 'unknown'}"
                title = f"{court} {year or ''}년 판결" if year else f"{court} 판결"
            
            # 기본 샘플 내용 생성 (실제 API 연동 시 대체 필요)
            sample_contents = {
                "사기": "피고인은 피해자들로부터 투자금을 편취한 사기 범죄로 기소되었다. 피고인은 피해자들에게 거짓 정보를 제공하여 재산상의 이익을 취득하였고, 피해회복이 되지 않아 초범임에도 불구하고 실형이 선고되었다.",
                "초범": "피고인은 초범으로서 범죄의 경중, 범행의 동기와 수단, 피해의 정도, 범행 후의 정황 등을 종합적으로 고려하여 집행유예를 선고받았다.",
                "집행유예": "피고인은 형법상 범죄를 저질렀으나, 초범이고 범죄의 경중이 크지 않으며, 범행 후 반성하고 피해회복을 위한 노력을 하고 있어 법원은 집행유예를 선고하였다.",
            }
            
            sample_holdings = {
                "사기": "초범이라도 피해 규모가 크고 피해회복이 되지 않으면 실형 선고 가능",
                "초범": "초범이 반성하고 피해회복 노력을 하면 집행유예 선고 가능",
                "집행유예": "초범이고 범죄 경중이 크지 않으며 반성과 피해회복 노력이 있으면 집행유예 선고 가능",
            }
            
            # 키워드에 맞는 샘플 내용 선택
            content = ""
            holding = ""
            if keywords and len(keywords) > 0:
                first_keyword = keywords[0]
                content = sample_contents.get(first_keyword, f"{first_keyword} 관련 판례 내용입니다.")
                holding = sample_holdings.get(first_keyword, f"{first_keyword} 관련 판결 요지입니다.")
            
            # year가 없으면 현재 연도 사용
            if year is None:
                year = datetime.now().year
            
            data = {
                "id": case_id,
                "category": "형사",  # 기본값, 실제로는 판례 내용 분석 필요
                "sub_category": keywords[0] if keywords and len(keywords) > 0 else "",
                "type": "case",
                "title": title,
                "content": content,
                "metadata": {
                    "court": court,
                    "year": year,
                    "case_number": case_number or "",
                    "keywords": keywords or [],
                    "holding": holding,
                    "updated_at": datetime.now().strftime("%Y-%m-%d"),
                },
            }
            
            return data
            
        except Exception as e:
            logger.error(f"판례 수집 실패: {str(e)}")
            return None
    
    def collect_from_file(
        self,
        file_path: Path,
    ) -> Optional[Dict[str, Any]]:
        """파일에서 판례 데이터를 읽습니다."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if self._validate_case_data(data):
                return data
            else:
                logger.warning(f"유효하지 않은 데이터: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"파일 읽기 실패: {str(e)}")
            return None
    
    def save_collected_data(
        self,
        data: Dict[str, Any],
        filename: Optional[str] = None,
    ) -> Path:
        """수집된 데이터를 저장합니다."""
        if filename is None:
            filename = f"{data['id']}.json"
        
        file_path = self.output_dir / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"판례 데이터 저장: {file_path}")
        return file_path
    
    def batch_collect_by_keywords(
        self,
        keywords: List[str],
        limit: int = 10,
    ) -> List[Path]:
        """
        키워드로 여러 판례를 배치로 수집합니다.
        
        Args:
            keywords: 검색 키워드 리스트
            limit: 키워드당 수집할 판례 수
            
        Returns:
            저장된 파일 경로 리스트
        """
        saved_files = []
        
        for keyword in keywords:
            data = self.collect_from_api(
                court="대법원",
                keywords=[keyword],
            )
            if data:
                file_path = self.save_collected_data(data)
                saved_files.append(file_path)
        
        logger.info(f"배치 수집 완료: {len(saved_files)}건")
        return saved_files
    
    def _validate_case_data(self, data: Dict[str, Any]) -> bool:
        """판례 데이터 검증"""
        required_fields = ["id", "type", "title", "content"]
        return all(field in data for field in required_fields) and data.get("type") == "case"

