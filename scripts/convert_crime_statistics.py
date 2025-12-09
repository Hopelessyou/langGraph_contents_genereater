"""범죄 통계 데이터 변환 스크립트

rag_crime_db_2025_dec 폴더의 범죄 통계 JSON 파일을
시스템 표준 형식으로 변환하여 statistics 폴더에 저장합니다.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.models.statistics import StatisticsModel, StatisticsMetadata


def convert_crime_statistics_file(input_file: Path, output_dir: Path) -> bool:
    """범죄 통계 파일을 변환하여 저장"""
    try:
        # 원본 파일 읽기
        with open(input_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        # 메타데이터 추출
        original_metadata = original_data.get('metadata', {})
        
        # StatisticsMetadata 생성
        stats_metadata = StatisticsMetadata(
            domain=original_data.get('domain', 'crime-statistics'),
            source=original_data.get('source', '경찰청 전국 범죄 발생 및 검거 현황'),
            date=original_data.get('date', '2025-12-31'),
            crime_category_main=original_metadata.get('범죄대분류', original_data.get('category', '')),
            crime_category_mid=original_metadata.get('범죄중분류'),
            crime_category_sub=original_metadata.get('범죄소분류'),
            occurrence=original_metadata.get('발생'),
            arrest=original_metadata.get('검거'),
            arrest_rate=original_metadata.get('검거율'),
            arrest_male=original_metadata.get('검거인원(남)'),
            arrest_female=original_metadata.get('검거인원(여)'),
            arrest_unknown=original_metadata.get('불상'),
            arrest_corporate=original_metadata.get('법인체'),
            tags=original_data.get('tags', []),
            embedding_text=original_data.get('embedding_text'),
            updated_at=original_data.get('date', '2025-12-31'),
        )
        
        # StatisticsModel 생성
        statistics_model = StatisticsModel(
            id=original_data.get('id', input_file.stem),
            category="형사",
            sub_category=original_metadata.get('범죄대분류', original_data.get('category', '기타')),
            type="statistics",
            title=original_data.get('title', '범죄 통계'),
            content=original_data.get('text', ''),
            metadata=stats_metadata,
        )
        
        # 출력 파일 경로 생성
        output_file = output_dir / f"{statistics_model.id}.json"
        
        # JSON 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(statistics_model.model_dump(), f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ 변환 실패: {input_file.name} - {str(e)}")
        return False


def convert_all_crime_statistics(input_dir: Path, output_dir: Path):
    """모든 범죄 통계 파일 변환"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 모든 JSON 파일 찾기
    json_files = list(input_dir.rglob('*.json'))
    
    if not json_files:
        print(f"⚠️  {input_dir}에서 JSON 파일을 찾을 수 없습니다.")
        return
    
    print(f"📁 총 {len(json_files)}개 파일 발견")
    print(f"📂 출력 디렉토리: {output_dir}")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for json_file in json_files:
        if convert_crime_statistics_file(json_file, output_dir):
            success_count += 1
            if success_count % 50 == 0:
                print(f"✅ 진행 중: {success_count}개 변환 완료...")
        else:
            fail_count += 1
    
    print("=" * 60)
    print(f"✅ 변환 완료: {success_count}개 성공, {fail_count}개 실패")
    print(f"📂 저장 위치: {output_dir}")


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="범죄 통계 데이터 변환")
    parser.add_argument(
        "--input-dir",
        type=str,
        default="data/collected/rag_crime_db_2025_dec",
        help="입력 디렉토리 경로 (기본값: data/collected/rag_crime_db_2025_dec)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/collected/statistics",
        help="출력 디렉토리 경로 (기본값: data/collected/statistics)"
    )
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    if not input_dir.exists():
        print(f"❌ 입력 디렉토리가 존재하지 않습니다: {input_dir}")
        return
    
    convert_all_crime_statistics(input_dir, output_dir)


if __name__ == "__main__":
    main()


