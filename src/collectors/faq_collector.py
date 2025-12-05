"""FAQ 데이터 수집 스크립트"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models import FAQModel

logger = logging.getLogger(__name__)


class FAQCollector:
    """FAQ 데이터 수집기"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("data/collected/faqs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_from_qa_pairs(
        self,
        qa_pairs: List[Dict[str, str]],
        category: str = "형사",
        sub_category: str = "",
    ) -> List[Dict[str, Any]]:
        """
        질문-답변 쌍에서 FAQ 데이터를 생성합니다.
        
        Args:
            qa_pairs: 질문-답변 쌍 리스트 [{"question": "...", "answer": "..."}]
            category: 카테고리
            sub_category: 하위 카테고리
            
        Returns:
            수집된 데이터 리스트
        """
        collected_data = []
        
        for i, qa in enumerate(qa_pairs):
            question = qa.get("question", "")
            answer = qa.get("answer", "")
            
            if not question or not answer:
                continue
            
            data = {
                "id": f"faq-{category}-{sub_category}-{i+1}",
                "category": category,
                "sub_category": sub_category,
                "type": "faq",
                "title": question[:50] + "..." if len(question) > 50 else question,
                "question": question,
                "content": answer,
                "metadata": {
                    "question_type": self._classify_question_type(question),
                    "related_topics": self._extract_topics(question, answer),
                    "frequency": qa.get("frequency", 0),
                    "updated_at": datetime.now().strftime("%Y-%m-%d"),
                },
            }
            
            if self._validate_faq_data(data):
                collected_data.append(data)
        
        logger.info(f"FAQ 수집 완료: {len(collected_data)}건")
        return collected_data
    
    def collect_from_file(
        self,
        file_path: Path,
    ) -> Optional[Dict[str, Any]]:
        """파일에서 FAQ 데이터를 읽습니다."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if self._validate_faq_data(data):
                return data
            else:
                logger.warning(f"유효하지 않은 데이터: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"파일 읽기 실패: {str(e)}")
            return None
    
    def collect_from_csv(
        self,
        csv_path: Path,
        question_column: str = "question",
        answer_column: str = "answer",
    ) -> List[Dict[str, Any]]:
        """
        CSV 파일에서 FAQ를 수집합니다.
        
        Args:
            csv_path: CSV 파일 경로
            question_column: 질문 컬럼명
            answer_column: 답변 컬럼명
            
        Returns:
            수집된 데이터 리스트
        """
        import csv
        
        qa_pairs = []
        
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    qa_pairs.append({
                        "question": row.get(question_column, ""),
                        "answer": row.get(answer_column, ""),
                    })
        except Exception as e:
            logger.error(f"CSV 읽기 실패: {str(e)}")
            return []
        
        return self.collect_from_qa_pairs(qa_pairs)
    
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
        
        logger.info(f"FAQ 데이터 저장: {file_path}")
        return file_path
    
    def _classify_question_type(self, question: str) -> str:
        """질문 타입 분류"""
        if any(keyword in question for keyword in ["처벌", "형량", "벌금", "징역"]):
            return "처벌"
        elif any(keyword in question for keyword in ["절차", "순서", "방법"]):
            return "절차"
        elif any(keyword in question for keyword in ["가능", "불가능", "할 수 있"]):
            return "가능성"
        else:
            return "일반"
    
    def _extract_topics(self, question: str, answer: str) -> List[str]:
        """질문과 답변에서 주제 추출"""
        topics = []
        common_topics = ["초범", "집행유예", "사기", "절도", "폭행", "계약"]
        
        text = question + " " + answer
        for topic in common_topics:
            if topic in text:
                topics.append(topic)
        
        return topics[:5]  # 최대 5개
    
    def _validate_faq_data(self, data: Dict[str, Any]) -> bool:
        """FAQ 데이터 검증"""
        required_fields = ["id", "type", "title", "question", "content"]
        return (
            all(field in data for field in required_fields)
            and data.get("type") == "faq"
        )

