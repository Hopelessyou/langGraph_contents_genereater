"""테스트용 더미 데이터 생성기"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from ..models import (
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


class DummyDataGenerator:
    """테스트용 더미 데이터 생성기"""
    
    def generate_statute(self, count: int = 5) -> List[Dict[str, Any]]:
        """법령 더미 데이터 생성"""
        data = []
        for i in range(1, count + 1):
            model = StatuteModel(
                id=f"statute-dummy-{i}",
                category="형사",
                sub_category="사기",
                type="statute",
                title=f"형법 제{300+i}조(더미 조문 {i})",
                content=f"더미 법령 조문 내용 {i}. 이는 테스트용 데이터입니다.",
                metadata={
                    "law_name": "형법",
                    "article_number": str(300 + i),
                    "topics": ["사기", "테스트"],
                    "source": "테스트",
                    "updated_at": datetime.now().strftime("%Y-%m-%d"),
                },
            )
            data.append(model.model_dump())
        return data
    
    def generate_case(self, count: int = 5) -> List[Dict[str, Any]]:
        """판례 더미 데이터 생성"""
        data = []
        for i in range(1, count + 1):
            model = CaseModel(
                id=f"case-dummy-{i}",
                category="형사",
                sub_category="사기",
                type="case",
                title=f"대법원 2024더{i} 판결",
                content=f"더미 판례 내용 {i}. 피고인은 사기 혐의로 기소되었습니다.",
                metadata={
                    "court": "대법원",
                    "year": 2024,
                    "case_number": f"2024더{i}",
                    "keywords": ["사기", "테스트"],
                    "holding": f"더미 판결 요지 {i}",
                    "updated_at": datetime.now().strftime("%Y-%m-%d"),
                },
            )
            data.append(model.model_dump())
        return data
    
    def generate_procedure(self, count: int = 3) -> List[Dict[str, Any]]:
        """절차 매뉴얼 더미 데이터 생성"""
        data = []
        stages = ["경찰조사", "검찰수사", "재판"]
        for i, stage in enumerate(stages[:count], 1):
            model = ProcedureModel(
                id=f"procedure-dummy-{i}",
                category="형사",
                sub_category="사기",
                type="procedure",
                title=f"사기 사건 {stage} 절차",
                content=f"1) 절차 시작 → 2) 조사/수사 → 3) 절차 종료",
                metadata={
                    "stage": stage,
                    "topic": "절차",
                    "keywords": [stage, "사기", "절차"],
                    "updated_at": datetime.now().strftime("%Y-%m-%d"),
                },
            )
            data.append(model.model_dump())
        return data
    
    def generate_template(self, count: int = 2) -> List[Dict[str, Any]]:
        """템플릿 더미 데이터 생성"""
        data = []
        for i in range(1, count + 1):
            model = TemplateModel(
                id=f"template-dummy-{i}",
                category="형사",
                sub_category="사기",
                type="template",
                title=f"사기 콘텐츠 템플릿 {i}",
                content=[
                    "1. 사건 요약",
                    "2. 관련 법령",
                    "3. 판례 경향",
                    "4. 결론",
                ],
                metadata={
                    "usage": "콘텐츠 생성 템플릿",
                    "output_styles": ["블로그형", "뉴스형"],
                    "updated_at": datetime.now().strftime("%Y-%m-%d"),
                },
            )
            data.append(model.model_dump())
        return data
    
    def generate_all(self, output_dir: Path | str) -> None:
        """
        모든 타입의 더미 데이터를 생성하여 저장합니다.
        
        Args:
            output_dir: 출력 디렉토리
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 각 타입별 더미 데이터 생성
        all_data = {
            "statute": self.generate_statute(),
            "case": self.generate_case(),
            "procedure": self.generate_procedure(),
            "template": self.generate_template(),
        }
        
        # 파일로 저장
        for doc_type, data_list in all_data.items():
            for data in data_list:
                file_path = output_dir / f"{data['id']}.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"더미 데이터 생성 완료: {output_dir}")
        print(f"  - 법령: {len(all_data['statute'])}건")
        print(f"  - 판례: {len(all_data['case'])}건")
        print(f"  - 절차: {len(all_data['procedure'])}건")
        print(f"  - 템플릿: {len(all_data['template'])}건")


if __name__ == "__main__":
    generator = DummyDataGenerator()
    generator.generate_all("data/dummy")

