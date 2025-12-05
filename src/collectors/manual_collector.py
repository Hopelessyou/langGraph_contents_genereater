"""매뉴얼 데이터 수집 스크립트"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models import ManualModel

logger = logging.getLogger(__name__)


class ManualCollector:
    """매뉴얼 데이터 수집기"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("data/collected/manuals")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_from_file(
        self,
        file_path: Path,
        manual_type: str = "변호 실무",
        category: str = "형사",
        sub_category: str = "",
    ) -> Optional[Dict[str, Any]]:
        """
        파일에서 매뉴얼 데이터를 읽습니다.
        
        Args:
            file_path: 파일 경로 (텍스트, 마크다운, PDF 등)
            manual_type: 매뉴얼 타입
            category: 카테고리
            sub_category: 하위 카테고리
            
        Returns:
            수집된 데이터 딕셔너리
        """
        try:
            # 파일 확장자에 따라 처리
            if file_path.suffix == ".json":
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif file_path.suffix in [".txt", ".md"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 파일명에서 정보 추출
                title = file_path.stem
                
                data = {
                    "id": f"manual-{file_path.stem}",
                    "category": category,
                    "sub_category": sub_category,
                    "type": "manual",
                    "title": title,
                    "content": content,
                    "metadata": {
                        "manual_type": manual_type,
                        "target_audience": "변호사",
                        "keywords": self._extract_keywords(content),
                        "updated_at": datetime.now().strftime("%Y-%m-%d"),
                    },
                }
            else:
                logger.warning(f"지원하지 않는 파일 형식: {file_path.suffix}")
                return None
            
            if self._validate_manual_data(data):
                return data
            else:
                logger.warning(f"유효하지 않은 데이터: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"파일 읽기 실패: {str(e)}")
            return None
    
    def collect_from_directory(
        self,
        directory: Path,
        pattern: str = "*.md",
    ) -> List[Dict[str, Any]]:
        """
        디렉토리에서 여러 매뉴얼을 수집합니다.
        
        Args:
            directory: 디렉토리 경로
            pattern: 파일 패턴
            
        Returns:
            수집된 데이터 리스트
        """
        collected_data = []
        
        for file_path in directory.glob(pattern):
            data = self.collect_from_file(file_path)
            if data:
                collected_data.append(data)
        
        logger.info(f"디렉토리 수집 완료: {len(collected_data)}건")
        return collected_data
    
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
        
        logger.info(f"매뉴얼 데이터 저장: {file_path}")
        return file_path
    
    def _extract_keywords(self, content: str) -> List[str]:
        """내용에서 키워드 추출 (간단한 구현)"""
        # 실제로는 더 정교한 키워드 추출 필요
        keywords = []
        common_terms = ["사기", "절도", "폭행", "계약", "손해배상"]
        
        for term in common_terms:
            if term in content:
                keywords.append(term)
        
        return keywords[:5]  # 최대 5개
    
    def _validate_manual_data(self, data: Dict[str, Any]) -> bool:
        """매뉴얼 데이터 검증"""
        required_fields = ["id", "type", "title", "content"]
        return all(field in data for field in required_fields) and data.get("type") == "manual"

