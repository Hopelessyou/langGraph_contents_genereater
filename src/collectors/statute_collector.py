"""법령 데이터 수집 스크립트"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Optional imports for web scraping (only needed if actually using API)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

from ..models import StatuteModel

logger = logging.getLogger(__name__)


class StatuteCollector:
    """법령 데이터 수집기"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("data/collected/statutes")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_from_api(
        self,
        law_name: str,
        article_number: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        법제처 API에서 법령 데이터를 수집합니다.
        
        Args:
            law_name: 법령명 (예: "형법")
            article_number: 조문 번호 (선택)
            
        Returns:
            수집된 데이터 딕셔너리
        """
        try:
            # 법제처 API 엔드포인트 (예시)
            # 실제 API는 법제처 공개 API를 사용해야 함
            base_url = "https://www.law.go.kr"
            
            # 여기서는 예시 구조만 제공
            # 실제 구현 시 법제처 API 문서 참고 필요
            
            data = {
                "id": f"statute-{law_name}-{article_number or 'all'}",
                "category": self._categorize_law(law_name),
                "sub_category": "",
                "type": "statute",
                "title": f"{law_name} 제{article_number}조" if article_number else law_name,
                "content": "",  # 실제 API에서 가져온 내용
                "metadata": {
                    "law_name": law_name,
                    "article_number": article_number or "",
                    "topics": [],
                    "source": "법제처",
                    "updated_at": datetime.now().strftime("%Y-%m-%d"),
                },
            }
            
            return data
            
        except Exception as e:
            logger.error(f"법령 수집 실패: {str(e)}")
            return None
    
    def collect_from_file(
        self,
        file_path: Path,
    ) -> Optional[Dict[str, Any]]:
        """
        파일에서 법령 데이터를 읽습니다.
        
        Args:
            file_path: 파일 경로
            
        Returns:
            수집된 데이터 딕셔너리
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 데이터 검증 및 변환
            if self._validate_statute_data(data):
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
        """
        수집된 데이터를 저장합니다.
        
        Args:
            data: 수집된 데이터
            filename: 저장할 파일명 (선택)
            
        Returns:
            저장된 파일 경로
        """
        if filename is None:
            filename = f"{data['id']}.json"
        
        file_path = self.output_dir / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"법령 데이터 저장: {file_path}")
        return file_path
    
    def batch_collect(
        self,
        law_names: List[str],
        article_numbers: Optional[List[str]] = None,
    ) -> List[Path]:
        """
        여러 법령을 배치로 수집합니다.
        
        Args:
            law_names: 법령명 리스트
            article_numbers: 조문 번호 리스트 (선택)
            
        Returns:
            저장된 파일 경로 리스트
        """
        saved_files = []
        
        for i, law_name in enumerate(law_names):
            article_number = article_numbers[i] if article_numbers and i < len(article_numbers) else None
            
            data = self.collect_from_api(law_name, article_number)
            if data:
                file_path = self.save_collected_data(data)
                saved_files.append(file_path)
        
        logger.info(f"배치 수집 완료: {len(saved_files)}건")
        return saved_files
    
    def _categorize_law(self, law_name: str) -> str:
        """법령명으로 카테고리 분류"""
        criminal_keywords = ["형법", "형사소송법", "특정경제범죄가중처벌법"]
        civil_keywords = ["민법", "민사소송법", "상법"]
        
        if any(keyword in law_name for keyword in criminal_keywords):
            return "형사"
        elif any(keyword in law_name for keyword in civil_keywords):
            return "민사"
        else:
            return "기타"
    
    def _validate_statute_data(self, data: Dict[str, Any]) -> bool:
        """법령 데이터 검증"""
        required_fields = ["id", "type", "title", "content"]
        return all(field in data for field in required_fields) and data.get("type") == "statute"

