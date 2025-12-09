#!/usr/bin/env python3
"""MD 문서들을 docs 폴더로 정리하는 스크립트"""

import shutil
from pathlib import Path

# 프로젝트 루트
project_root = Path(__file__).parent.parent

# 폴더 생성
guides_dir = project_root / "docs" / "guides"
project_dir = project_root / "docs" / "project"
guides_dir.mkdir(parents=True, exist_ok=True)
project_dir.mkdir(parents=True, exist_ok=True)

# 가이드 문서들 (docs/guides/로 이동)
guide_files = [
    "CHECK_INDEXED_DATA.md",
    "POWERSHELL_USAGE.md",
    "DATA_PREPROCESSING_CODE_EXAMPLES.md",
    "DATA_PREPROCESSING_EASY_GUIDE.md",
    "DOCUMENT_VALIDATOR_GUIDE.md",
    "RAG_FILE_SAVE_GUIDE.md",
    "SWAGGER_UI_GUIDE.md",
    "USAGE_GUIDE.md",
    "RAG_DATA_PROCESSING_GUIDE.md",
    "RAG_DATA_BUILD_GUIDE.md",
    "DOCKER_VS_LOCAL.md",
]

# 프로젝트 문서들 (docs/project/로 이동)
project_files = [
    "CODE_ANALYSIS.md",
    "CODE_ANALYSIS_UPDATED.md",
    "NEXT_STEPS.md",
    "제작_순서_계획서.md",
    "제작_순서_요약.md",
    "진행_상황_요약.md",
    "최종_완료_요약.md",
    "ANALYSIS_판례파싱결과.md",
]

print("=" * 60)
print("📁 MD 문서 정리 시작")
print("=" * 60)

# 가이드 문서 이동
moved_guides = 0
for filename in guide_files:
    source = project_root / filename
    if source.exists():
        dest = guides_dir / filename
        shutil.move(str(source), str(dest))
        print(f"✅ {filename} → docs/guides/")
        moved_guides += 1
    else:
        print(f"⚠️  {filename} 파일을 찾을 수 없습니다.")

# 프로젝트 문서 이동
moved_projects = 0
for filename in project_files:
    source = project_root / filename
    if source.exists():
        dest = project_dir / filename
        shutil.move(str(source), str(dest))
        print(f"✅ {filename} → docs/project/")
        moved_projects += 1
    else:
        print(f"⚠️  {filename} 파일을 찾을 수 없습니다.")

print("\n" + "=" * 60)
print(f"📊 정리 완료!")
print(f"   가이드 문서: {moved_guides}개 이동")
print(f"   프로젝트 문서: {moved_projects}개 이동")
print("=" * 60)
print(f"\n📁 폴더 구조:")
print(f"   docs/guides/     - 사용 가이드 문서")
print(f"   docs/project/   - 프로젝트 관련 문서")
print(f"   README.md       - 프로젝트 루트에 유지")

