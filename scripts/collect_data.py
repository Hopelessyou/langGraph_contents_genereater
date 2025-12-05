"""데이터 수집 스크립트"""

import sys
import argparse
from pathlib import Path

from src.collectors import (
    StatuteCollector,
    CaseCollector,
    ManualCollector,
    FAQCollector,
)


def collect_statutes(output_dir: Path):
    """법령 데이터 수집"""
    print("법령 데이터 수집 시작...")
    collector = StatuteCollector(output_dir=output_dir / "statutes")
    
    # 예시: 형법 주요 조문 수집
    law_names = ["형법", "형사소송법"]
    article_numbers = ["347", "250"]
    
    saved_files = collector.batch_collect(law_names, article_numbers)
    print(f"법령 데이터 수집 완료: {len(saved_files)}건")


def collect_cases(output_dir: Path):
    """판례 데이터 수집"""
    print("판례 데이터 수집 시작...")
    collector = CaseCollector(output_dir=output_dir / "cases")
    
    # 예시: 키워드로 판례 수집
    keywords = ["사기", "초범", "집행유예"]
    saved_files = collector.batch_collect_by_keywords(keywords)
    print(f"판례 데이터 수집 완료: {len(saved_files)}건")


def collect_manuals(output_dir: Path, source_dir: Path):
    """매뉴얼 데이터 수집"""
    print("매뉴얼 데이터 수집 시작...")
    collector = ManualCollector(output_dir=output_dir / "manuals")
    
    if source_dir.exists():
        collected_data = collector.collect_from_directory(source_dir, "*.md")
        for data in collected_data:
            collector.save_collected_data(data)
        print(f"매뉴얼 데이터 수집 완료: {len(collected_data)}건")
    else:
        print(f"소스 디렉토리가 존재하지 않습니다: {source_dir}")


def collect_faqs(output_dir: Path, source_file: Path = None):
    """FAQ 데이터 수집"""
    print("FAQ 데이터 수집 시작...")
    collector = FAQCollector(output_dir=output_dir / "faqs")
    
    if source_file and source_file.exists():
        if source_file.suffix == ".csv":
            collected_data = collector.collect_from_csv(source_file)
        else:
            data = collector.collect_from_file(source_file)
            collected_data = [data] if data else []
        
        for data in collected_data:
            collector.save_collected_data(data)
        print(f"FAQ 데이터 수집 완료: {len(collected_data)}건")
    else:
        # 예시 FAQ 생성
        qa_pairs = [
            {
                "question": "사기 초범은 집행유예가 가능한가요?",
                "answer": "사기 초범이라도 피해 규모가 크면 집행유예가 어려울 수 있습니다.",
            },
            {
                "question": "사기 사건의 처벌은 어떻게 되나요?",
                "answer": "형법 제347조에 따라 10년 이하의 징역 또는 2천만원 이하의 벌금에 처합니다.",
            },
        ]
        
        collected_data = collector.collect_from_qa_pairs(qa_pairs)
        for data in collected_data:
            collector.save_collected_data(data)
        print(f"FAQ 데이터 수집 완료: {len(collected_data)}건")


def main():
    parser = argparse.ArgumentParser(description="법률 데이터 수집 스크립트")
    parser.add_argument(
        "--type",
        choices=["statute", "case", "manual", "faq", "all"],
        default="all",
        help="수집할 데이터 타입",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/collected"),
        help="출력 디렉토리",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        help="소스 디렉토리 (매뉴얼용)",
    )
    parser.add_argument(
        "--source-file",
        type=Path,
        help="소스 파일 (FAQ용)",
    )
    
    args = parser.parse_args()
    
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.type == "statute" or args.type == "all":
        collect_statutes(args.output_dir)
    
    if args.type == "case" or args.type == "all":
        collect_cases(args.output_dir)
    
    if args.type == "manual" or args.type == "all":
        source_dir = args.source_dir or Path("data/sources/manuals")
        collect_manuals(args.output_dir, source_dir)
    
    if args.type == "faq" or args.type == "all":
        collect_faqs(args.output_dir, args.source_file)
    
    print("데이터 수집 완료!")


if __name__ == "__main__":
    main()

