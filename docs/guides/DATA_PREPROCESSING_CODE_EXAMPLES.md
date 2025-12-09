# 데이터 전처리 코드 예시 📝

실제로 사용할 수 있는 데이터 전처리 코드 예시입니다.

---

## 목차

1. [가장 쉬운 방법: 스크립트 사용](#1-가장-쉬운-방법-스크립트-사용)
2. [Python 코드로 직접 실행](#2-python-코드로-직접-실행)
3. [단계별로 직접 실행](#3-단계별로-직접-실행)
4. [실전 예제](#4-실전-예제)

---

## 1. 가장 쉬운 방법: 스크립트 사용

### 1.1 기본 사용법

```bash
# 법령 데이터 전처리
python scripts/process_and_index.py \
    --input-dir "data/collected/statutes" \
    --doc-type "statute"

# 판례 데이터 전처리
python scripts/process_and_index.py \
    --input-dir "data/collected/cases" \
    --doc-type "case"
```

### 1.2 옵션 설명

```bash
# 전체 옵션 보기
python scripts/process_and_index.py --help

# 출력 디렉토리 지정
python scripts/process_and_index.py \
    --input-dir "data/collected/statutes" \
    --output-dir "data/processed/statutes" \
    --doc-type "statute"

# 전처리만 수행 (인덱싱 건너뛰기)
python scripts/process_and_index.py \
    --input-dir "data/collected/statutes" \
    --doc-type "statute" \
    --skip-index

# 인덱싱만 수행 (전처리 건너뛰기)
python scripts/process_and_index.py \
    --input-dir "data/processed/statutes" \
    --doc-type "statute" \
    --skip-process
```

### 1.3 Windows PowerShell 사용법

```powershell
# PowerShell에서 실행
python scripts/process_and_index.py `
    --input-dir "data/collected/statutes" `
    --doc-type "statute"
```

---

## 2. Python 코드로 직접 실행

### 2.1 기본 예제: 디렉토리 전체 처리

```python
#!/usr/bin/env python3
"""데이터 전처리 기본 예제"""

from src.processors.pipeline import BatchProcessor
from pathlib import Path

# 전처리기 생성
processor = BatchProcessor()

# 전처리 실행
results = processor.process_directory(
    input_dir="data/collected/statutes",      # 원본 데이터 위치
    output_dir="data/processed/statutes",     # 저장할 위치
    doc_type="statute",                       # 문서 타입
    clean=True,                               # 정제 수행
    validate=True,                            # 검증 수행
    remove_duplicates=True,                   # 중복 제거
)

# 결과 확인
total = len(results)
success = sum(1 for success, _ in results.values() if success)
failed = total - success

print(f"\n📊 처리 결과:")
print(f"   총 파일: {total}개")
print(f"   ✅ 성공: {success}개")
print(f"   ❌ 실패: {failed}개")

# 실패한 파일 목록
if failed > 0:
    print(f"\n⚠️  실패한 파일:")
    for filename, (success, error) in results.items():
        if not success:
            print(f"   - {filename}: {error}")
```

### 2.2 단일 파일 처리

```python
from src.processors.pipeline import BatchProcessor
from pathlib import Path

processor = BatchProcessor()

# 단일 파일 처리
success, error = processor.process_file(
    input_path="data/collected/statutes/형법/statute-형법-347.json",
    output_path="data/processed/statutes/statute-형법-347.json",
    doc_type="statute",
    clean=True,
    validate=True,
)

if success:
    print("✅ 파일 처리 성공!")
else:
    print(f"❌ 파일 처리 실패: {error}")
```

### 2.3 여러 문서 타입 일괄 처리

```python
from src.processors.pipeline import BatchProcessor

processor = BatchProcessor()

# 처리할 문서 타입 목록
doc_types = {
    "statute": "data/collected/statutes",
    "case": "data/collected/cases",
    "procedure": "data/collected/procedures",
}

# 각 타입별로 처리
for doc_type, input_dir in doc_types.items():
    print(f"\n{'='*60}")
    print(f"처리 중: {doc_type}")
    print(f"{'='*60}")
    
    results = processor.process_directory(
        input_dir=input_dir,
        output_dir=f"data/processed/{doc_type}",
        doc_type=doc_type,
        clean=True,
        validate=True,
        remove_duplicates=True,
    )
    
    # 통계 출력
    total = len(results)
    success = sum(1 for s, _ in results.values() if s)
    print(f"✅ {doc_type}: {success}/{total} 성공")
```

---

## 3. 단계별로 직접 실행

### 3.1 전체 단계 포함 예제

```python
#!/usr/bin/env python3
"""단계별 데이터 전처리 예제"""

from src.processors.validator import DocumentValidator
from src.processors.cleaner import DataCleaner
from src.processors.converter import JSONConverter
from pathlib import Path
import json

def preprocess_single_file(input_file: Path, output_file: Path, doc_type: str):
    """단일 파일을 단계별로 전처리"""
    
    print(f"📄 처리 중: {input_file.name}")
    
    # 1. 원본 데이터 읽기
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        print("   ✅ 파일 읽기 완료")
    except Exception as e:
        print(f"   ❌ 파일 읽기 실패: {e}")
        return False
    
    # 2. 형식 변환
    converter = JSONConverter()
    standard_data = converter.convert_to_standard_format(raw_data, doc_type)
    
    if not standard_data:
        print("   ❌ 형식 변환 실패")
        return False
    print("   ✅ 형식 변환 완료")
    
    # 3. 데이터 정제
    cleaner = DataCleaner()
    cleaned_data = cleaner.clean(standard_data)
    print("   ✅ 데이터 정제 완료")
    
    # 4. 필수 필드 검증
    valid, errors = cleaner.validate_required_fields(cleaned_data)
    if not valid:
        print(f"   ❌ 필수 필드 검증 실패: {', '.join(errors)}")
        return False
    print("   ✅ 필수 필드 검증 완료")
    
    # 5. 최종 검증
    validator = DocumentValidator()
    success, model = validator.validate(cleaned_data)
    
    if not success:
        print(f"   ❌ 최종 검증 실패:")
        for error in validator.get_errors():
            print(f"      - {error}")
        return False
    print("   ✅ 최종 검증 완료")
    
    # 6. 저장
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(model.model_dump(), f, ensure_ascii=False, indent=2)
        print(f"   ✅ 저장 완료: {output_file.name}")
        return True
    except Exception as e:
        print(f"   ❌ 저장 실패: {e}")
        return False


# 사용 예제
if __name__ == "__main__":
    input_file = Path("data/collected/statutes/형법/statute-형법-347.json")
    output_file = Path("data/processed/statutes/statute-형법-347.json")
    
    success = preprocess_single_file(input_file, output_file, "statute")
    
    if success:
        print("\n✅ 전처리 완료!")
    else:
        print("\n❌ 전처리 실패!")
```

### 3.2 각 단계별 상세 예제

```python
from src.processors.validator import DocumentValidator
from src.processors.cleaner import DataCleaner
from src.processors.converter import JSONConverter
import json

# 원본 데이터
raw_data = {
    "법률명": "형법",
    "조문번호": "347",
    "제목": "  형법 제347조  ",
    "내용": "사기죄의   내용입니다.\n\n\n여러 줄바꿈",
}

# 1단계: 형식 변환
converter = JSONConverter()
standard_data = converter.convert_to_standard_format(raw_data, "statute")
print("1단계 완료: 형식 변환")
print(json.dumps(standard_data, ensure_ascii=False, indent=2))

# 2단계: 데이터 정제
cleaner = DataCleaner()
cleaned_data = cleaner.clean(standard_data)
print("\n2단계 완료: 데이터 정제")
print(json.dumps(cleaned_data, ensure_ascii=False, indent=2))

# 3단계: 검증
validator = DocumentValidator()
success, model = validator.validate(cleaned_data)

if success:
    print("\n3단계 완료: 검증 성공")
    print(f"문서 ID: {model.id}")
    print(f"제목: {model.title}")
else:
    print("\n3단계 실패: 검증 실패")
    for error in validator.get_errors():
        print(f"  - {error}")
```

---

## 4. 실전 예제

### 4.1 완전한 전처리 스크립트

```python
#!/usr/bin/env python3
"""완전한 데이터 전처리 스크립트"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.processors.pipeline import BatchProcessor
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

def main():
    """메인 함수"""
    processor = BatchProcessor()
    
    # 처리할 데이터 목록
    data_configs = [
        {
            "name": "법령",
            "input_dir": "data/collected/statutes",
            "output_dir": "data/processed/statutes",
            "doc_type": "statute",
        },
        {
            "name": "판례",
            "input_dir": "data/collected/cases",
            "output_dir": "data/processed/cases",
            "doc_type": "case",
        },
    ]
    
    # 전체 통계
    total_files = 0
    total_success = 0
    total_failed = 0
    
    # 각 데이터 타입별로 처리
    for config in data_configs:
        print(f"\n{'='*60}")
        print(f"📚 {config['name']} 데이터 전처리")
        print(f"{'='*60}")
        
        input_dir = Path(config['input_dir'])
        if not input_dir.exists():
            print(f"⚠️  입력 디렉토리가 없습니다: {input_dir}")
            continue
        
        # 전처리 실행
        results = processor.process_directory(
            input_dir=config['input_dir'],
            output_dir=config['output_dir'],
            doc_type=config['doc_type'],
            clean=True,
            validate=True,
            remove_duplicates=True,
        )
        
        # 통계 계산
        total = len(results)
        success = sum(1 for s, _ in results.values() if s)
        failed = total - success
        
        total_files += total
        total_success += success
        total_failed += failed
        
        # 결과 출력
        print(f"\n📊 {config['name']} 처리 결과:")
        print(f"   총 파일: {total}개")
        print(f"   ✅ 성공: {success}개")
        print(f"   ❌ 실패: {failed}개")
        
        # 실패한 파일 목록
        if failed > 0:
            print(f"\n⚠️  실패한 파일:")
            for filename, (s, error) in results.items():
                if not s:
                    print(f"   - {filename}: {error}")
    
    # 전체 통계 출력
    print(f"\n{'='*60}")
    print(f"📊 전체 처리 결과")
    print(f"{'='*60}")
    print(f"   총 파일: {total_files}개")
    print(f"   ✅ 성공: {total_success}개")
    print(f"   ❌ 실패: {total_failed}개")
    print(f"   성공률: {total_success/total_files*100:.1f}%" if total_files > 0 else "   성공률: 0%")

if __name__ == "__main__":
    main()
```

### 4.2 에러 처리 포함 예제

```python
from src.processors.pipeline import BatchProcessor
from pathlib import Path
import json

def preprocess_with_error_handling(input_dir: str, output_dir: str, doc_type: str):
    """에러 처리를 포함한 전처리"""
    
    processor = BatchProcessor()
    
    try:
        # 전처리 실행
        results = processor.process_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            doc_type=doc_type,
            clean=True,
            validate=True,
            remove_duplicates=True,
        )
        
        # 성공/실패 분류
        success_files = []
        failed_files = []
        
        for filename, (success, error) in results.items():
            if success:
                success_files.append(filename)
            else:
                failed_files.append((filename, error))
        
        # 결과 리포트 생성
        report = {
            "total": len(results),
            "success": len(success_files),
            "failed": len(failed_files),
            "success_files": success_files,
            "failed_files": [
                {"filename": f, "error": e} for f, e in failed_files
            ],
        }
        
        # 리포트 저장
        report_file = Path(output_dir) / "preprocessing_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 전처리 완료!")
        print(f"   성공: {report['success']}/{report['total']}")
        print(f"   리포트 저장: {report_file}")
        
        return report
        
    except Exception as e:
        print(f"❌ 전처리 중 오류 발생: {e}")
        raise


# 사용 예제
if __name__ == "__main__":
    report = preprocess_with_error_handling(
        input_dir="data/collected/statutes",
        output_dir="data/processed/statutes",
        doc_type="statute",
    )
```

### 4.3 진행 상황 표시 예제

```python
from src.processors.pipeline import BatchProcessor
from pathlib import Path
from tqdm import tqdm  # pip install tqdm 필요

def preprocess_with_progress(input_dir: str, output_dir: str, doc_type: str):
    """진행 상황을 표시하는 전처리"""
    
    processor = BatchProcessor()
    input_path = Path(input_dir)
    
    # 처리할 파일 목록
    json_files = list(input_path.rglob("*.json"))
    
    if not json_files:
        print("⚠️  처리할 파일이 없습니다.")
        return
    
    print(f"📁 총 {len(json_files)}개 파일 처리 시작...\n")
    
    results = {}
    
    # 진행 상황 표시
    for json_file in tqdm(json_files, desc="전처리 진행"):
        relative_path = json_file.relative_to(input_path)
        output_file = Path(output_dir) / relative_path
        
        success, error = processor.process_file(
            input_path=json_file,
            output_path=output_file,
            doc_type=doc_type,
            clean=True,
            validate=True,
        )
        
        results[json_file.name] = (success, error)
    
    # 결과 출력
    total = len(results)
    success = sum(1 for s, _ in results.values() if s)
    failed = total - success
    
    print(f"\n📊 처리 결과:")
    print(f"   ✅ 성공: {success}개")
    print(f"   ❌ 실패: {failed}개")
    
    return results


# 사용 예제
if __name__ == "__main__":
    preprocess_with_progress(
        input_dir="data/collected/statutes",
        output_dir="data/processed/statutes",
        doc_type="statute",
    )
```

### 4.4 재귀적으로 하위 디렉토리 처리

```python
from src.processors.pipeline import BatchProcessor
from pathlib import Path

def preprocess_recursive(input_dir: str, output_dir: str, doc_type: str):
    """하위 디렉토리를 포함하여 재귀적으로 처리"""
    
    processor = BatchProcessor()
    input_path = Path(input_dir)
    
    # 모든 JSON 파일 찾기 (하위 디렉토리 포함)
    json_files = list(input_path.rglob("*.json"))
    
    print(f"📁 총 {len(json_files)}개 파일 발견\n")
    
    results = {}
    
    for json_file in json_files:
        # 상대 경로 유지
        relative_path = json_file.relative_to(input_path)
        output_file = Path(output_dir) / relative_path
        
        print(f"처리 중: {relative_path}")
        
        success, error = processor.process_file(
            input_path=json_file,
            output_path=output_file,
            doc_type=doc_type,
            clean=True,
            validate=True,
        )
        
        results[str(relative_path)] = (success, error)
        
        if success:
            print(f"  ✅ 성공\n")
        else:
            print(f"  ❌ 실패: {error}\n")
    
    return results


# 사용 예제
if __name__ == "__main__":
    # 하위 디렉토리 구조 유지하면서 처리
    # data/collected/statutes/형법/statute-347.json
    # → data/processed/statutes/형법/statute-347.json
    preprocess_recursive(
        input_dir="data/collected/statutes",
        output_dir="data/processed/statutes",
        doc_type="statute",
    )
```

---

## 빠른 참조

### 가장 간단한 사용법

```python
from src.processors.pipeline import BatchProcessor

processor = BatchProcessor()
results = processor.process_directory(
    input_dir="data/collected/statutes",
    output_dir="data/processed/statutes",
    doc_type="statute",
)
```

### 명령줄에서 실행

```bash
python scripts/process_and_index.py \
    --input-dir "data/collected/statutes" \
    --doc-type "statute"
```

---

## 문제 해결

### Q: "ModuleNotFoundError: No module named 'src'" 에러

**해결 방법:**
```python
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
```

### Q: "파일이 존재하지 않습니다" 에러

**해결 방법:**
```python
from pathlib import Path

input_dir = Path("data/collected/statutes")
if not input_dir.exists():
    print(f"⚠️  디렉토리가 없습니다: {input_dir}")
    print("   먼저 데이터를 수집하세요.")
```

### Q: "검증 실패" 에러

**해결 방법:**
```python
from src.processors.validator import DocumentValidator

validator = DocumentValidator()
success, model = validator.validate(data)

if not success:
    # 에러 확인
    for error in validator.get_errors():
        print(f"  - {error}")
    
    # 데이터 수정 후 다시 시도
```

---

**더 자세한 내용은 다음 문서를 참고하세요:**
- [데이터 전처리 쉽게 이해하기](./DATA_PREPROCESSING_EASY_GUIDE.md)
- [DocumentValidator 사용 가이드](./DOCUMENT_VALIDATOR_GUIDE.md)
- [RAG 데이터 처리 가이드](./RAG_DATA_PROCESSING_GUIDE.md)

