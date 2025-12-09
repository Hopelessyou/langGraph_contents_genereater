# 데이터 전처리 쉽게 이해하기 🧹

법률 AI 시스템에서 데이터 전처리는 **"원시 데이터를 깨끗하고 사용하기 좋은 형태로 정리하는 과정"**입니다.

마치 요리를 하기 전에 재료를 손질하는 것과 같아요! 🍳

---

## 📖 목차

1. [데이터 전처리가 뭔가요?](#데이터-전처리가-뭔가요)
2. [왜 필요한가요?](#왜-필요한가요)
3. [전처리 과정 단계별 설명](#전처리-과정-단계별-설명)
4. [실제 사용 예시](#실제-사용-예시)
5. [자주 묻는 질문](#자주-묻는-질문)

---

## 데이터 전처리가 뭔가요?

### 간단한 비유로 이해하기

**데이터 전처리 = 요리 재료 손질하기**

```
원시 데이터 (수집된 법률 문서)
    ↓
[전처리 과정]
    ↓
깨끗한 데이터 (AI가 사용할 수 있는 형태)
```

예를 들어:
- 🥬 **채소 손질**: 불필요한 부분 제거, 깨끗이 씻기
- 🥩 **고기 손질**: 지방 제거, 적절한 크기로 자르기
- 🧂 **양념 준비**: 적절한 양으로 조절하기

데이터 전처리도 마찬가지입니다:
- 📄 **불필요한 정보 제거**: 공백, 특수문자 정리
- ✅ **형식 통일**: 모든 문서를 같은 형식으로 만들기
- 🔍 **검증**: 필요한 정보가 모두 있는지 확인하기

---

## 왜 필요한가요?

### 문제 상황 예시

**전처리 전 데이터:**
```json
{
  "id": "statute-347",
  "title": "  형법 제347조  ",  ← 앞뒤 공백 있음
  "content": "사기죄의   내용입니다.\n\n\n여러 줄바꿈",  ← 공백, 줄바꿈 많음
  "metadata": {
    "law_name": "형법",
    "article_number": "347"
  }
}
```

**문제점:**
- ❌ 앞뒤 공백이 있어서 검색이 어려움
- ❌ 불필요한 공백과 줄바꿈이 많아서 데이터 크기만 큼
- ❌ AI가 이해하기 어려운 형태

**전처리 후 데이터:**
```json
{
  "id": "statute-347",
  "title": "형법 제347조",  ← 깨끗하게 정리됨
  "content": "사기죄의 내용입니다. 여러 줄바꿈",  ← 정리됨
  "metadata": {
    "law_name": "형법",
    "article_number": "347"
  }
}
```

**개선점:**
- ✅ 깨끗하게 정리되어 검색이 쉬움
- ✅ 데이터 크기가 작아져서 처리 속도가 빨라짐
- ✅ AI가 이해하기 쉬운 형태

---

## 전처리 과정 단계별 설명

### 전체 흐름도

```
[1단계] 수집된 원시 데이터
    ↓
[2단계] 형식 변환 (JSONConverter)
    ↓
[3단계] 데이터 정제 (DataCleaner)
    ↓
[4단계] 데이터 검증 (DocumentValidator)
    ↓
[5단계] 중복 제거
    ↓
[6단계] 최종 저장
```

### 1단계: 수집된 원시 데이터

**무엇을 하나요?**
- PDF에서 추출한 법률 문서
- 웹사이트에서 수집한 판례
- 수동으로 입력한 데이터

**예시:**
```
data/collected/statutes/
├── 형법/
│   ├── statute-형법-1.json
│   ├── statute-형법-347.json
│   └── ...
└── 형사소송법/
    └── ...
```

**특징:**
- 📄 다양한 형식으로 저장되어 있음
- 🎨 일관성이 없을 수 있음
- 🐛 오타나 누락이 있을 수 있음

---

### 2단계: 형식 변환 (JSONConverter)

**무엇을 하나요?**
- 다양한 형식의 데이터를 **표준 형식**으로 통일

**비유:** 
- 모든 요리 재료를 같은 크기의 그릇에 담기
- 모든 문서를 같은 형식의 JSON으로 만들기

**변환 전:**
```json
{
  "법률명": "형법",
  "조문번호": "347",
  "제목": "사기죄",
  "내용": "사기죄의 내용..."
}
```

**변환 후 (표준 형식):**
```json
{
  "id": "statute-형법-347",
  "type": "statute",
  "category": "형사",
  "sub_category": "사기",
  "title": "형법 제347조(사기)",
  "content": "사기죄의 내용...",
  "metadata": {
    "law_name": "형법",
    "article_number": "347"
  }
}
```

**왜 필요한가요?**
- ✅ 모든 문서가 같은 형식을 따르면 처리하기 쉬움
- ✅ AI가 일관되게 이해할 수 있음
- ✅ 나중에 수정하거나 추가하기 편함

---

### 3단계: 데이터 정제 (DataCleaner)

**무엇을 하나요?**
- 불필요한 공백, 특수문자 제거
- 텍스트 정규화 (전각/반각 통일)
- 빈 필드 정리

**비유:**
- 채소의 썩은 부분 제거
- 과일의 껍질 벗기기
- 재료의 불필요한 부분 정리

#### 3.1 공백 정제

**문제:**
```
"title": "  형법 제347조  "  ← 앞뒤 공백
"content": "사기죄의   내용입니다"  ← 중간에 여러 공백
```

**정제 후:**
```
"title": "형법 제347조"  ← 공백 제거
"content": "사기죄의 내용입니다"  ← 공백 정리
```

#### 3.2 특수문자 정제

**문제:**
```
"content": "사기죄의 내용입니다.\x00\x01"  ← 제어 문자 포함
```

**정제 후:**
```
"content": "사기죄의 내용입니다."  ← 제어 문자 제거
```

#### 3.3 텍스트 정규화

**문제:**
```
"title": "형법 제347조（사기）"  ← 전각 괄호
```

**정제 후:**
```
"title": "형법 제347조(사기)"  ← 반각 괄호로 통일
```

---

### 4단계: 데이터 검증 (DocumentValidator)

**무엇을 하나요?**
- 필요한 정보가 모두 있는지 확인
- 데이터 형식이 올바른지 확인
- 문서 타입별 필수 필드 확인

**비유:**
- 요리 재료가 모두 준비되었는지 확인
- 재료가 신선한지 확인
- 필요한 양이 충분한지 확인

#### 4.1 필수 필드 확인

**필수 필드:**
- `id`: 문서 고유 번호
- `type`: 문서 타입 (statute, case 등)
- `title`: 제목
- `content`: 내용
- `category`: 카테고리

**검증 예시:**
```python
# ✅ 올바른 데이터
{
  "id": "statute-347",
  "type": "statute",
  "title": "형법 제347조",
  "content": "내용...",
  "category": "형사"
}
# → 검증 성공! ✅

# ❌ 잘못된 데이터
{
  "id": "statute-347",
  # "type" 필드가 없음!
  "title": "형법 제347조"
}
# → 검증 실패! ❌ (에러: 'type' 필드가 없습니다)
```

#### 4.2 데이터 타입 확인

**검증 예시:**
```python
# ✅ 올바른 타입
{
  "id": "statute-347",  # 문자열 ✅
  "type": "statute"     # 문자열 ✅
}

# ❌ 잘못된 타입
{
  "id": 347,  # 숫자 ❌ (문자열이어야 함)
  "type": "statute"
}
# → 검증 실패! ❌ (에러: id는 문자열이어야 합니다)
```

#### 4.3 문서 타입별 검증

**법령 (statute)의 경우:**
- `metadata.law_name` 필수
- `metadata.article_number` 필수

**판례 (case)의 경우:**
- `metadata.court` 필수
- `metadata.year` 필수

**검증 예시:**
```python
# ✅ 올바른 법령 데이터
{
  "type": "statute",
  "metadata": {
    "law_name": "형법",      # ✅ 필수 필드
    "article_number": "347"  # ✅ 필수 필드
  }
}

# ❌ 잘못된 법령 데이터
{
  "type": "statute",
  "metadata": {
    # "law_name"이 없음! ❌
    "article_number": "347"
  }
}
# → 검증 실패! ❌
```

---

### 5단계: 중복 제거

**무엇을 하나요?**
- 같은 문서가 여러 번 저장되어 있는지 확인
- 중복된 문서 제거

**비유:**
- 같은 재료를 여러 번 준비한 경우 하나만 남기기

**예시:**
```
원본 파일들:
- statute-형법-347.json  (내용: "형법 제347조...")
- statute-형법-347-copy.json  (내용: "형법 제347조...")  ← 중복!

중복 제거 후:
- statute-형법-347.json  (하나만 남김)
```

**중복 확인 방법:**
- 문서 ID가 같은지 확인
- 내용이 완전히 같은지 확인

---

### 6단계: 최종 저장

**무엇을 하나요?**
- 전처리가 완료된 데이터를 `data/processed/` 폴더에 저장

**저장 위치:**
```
data/
├── collected/     ← 원시 데이터 (전처리 전)
│   └── statutes/
│       └── ...
└── processed/     ← 전처리된 데이터 (전처리 후)
    └── statutes/
        └── ...
```

**왜 분리하나요?**
- ✅ 원본 데이터는 그대로 보존
- ✅ 전처리된 데이터만 사용
- ✅ 문제 발생 시 원본으로 돌아갈 수 있음

---

## 실제 사용 예시

### 예시 1: 간단한 전처리 (스크립트 사용)

**가장 쉬운 방법!** 🎯

```bash
# 법령 데이터 전처리
python scripts/process_and_index.py \
    --input-dir "data/collected/statutes" \
    --doc-type "statute"
```

**이 명령어가 하는 일:**
1. `data/collected/statutes/` 폴더의 모든 JSON 파일 읽기
2. 형식 변환 → 정제 → 검증 → 중복 제거
3. `data/processed/statutes/` 폴더에 저장

**결과:**
```
✅ 전처리 완료: 150/150 파일
📁 저장 위치: data/processed/statutes/
```

---

### 예시 2: Python 코드로 직접 실행

**더 세밀한 제어가 필요한 경우** 🔧

```python
from src.processors.pipeline import BatchProcessor
from pathlib import Path

# 전처리기 생성
processor = BatchProcessor()

# 전처리 실행
results = processor.process_directory(
    input_dir="data/collected/statutes",  # 원본 데이터 위치
    output_dir="data/processed/statutes",  # 저장할 위치
    doc_type="statute",                    # 문서 타입
    clean=True,                            # 정제 수행
    validate=True,                         # 검증 수행
    remove_duplicates=True,                # 중복 제거
)

# 결과 확인
print(f"✅ 성공: {results['success']}개")
print(f"❌ 실패: {results['failed']}개")
print(f"📊 총 파일: {results['total']}개")
```

---

### 예시 3: 단계별로 직접 실행

**각 단계를 개별적으로 실행하고 싶은 경우** 🎨

```python
from src.processors.validator import DocumentValidator
from src.processors.cleaner import DataCleaner
from src.processors.converter import JSONConverter
import json

# 1. 원본 데이터 읽기
with open("data/collected/statutes/statute-347.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# 2. 형식 변환
converter = JSONConverter()
standard_data = converter.convert_to_standard_format(raw_data, "statute")

# 3. 데이터 정제
cleaner = DataCleaner()
cleaned_data = cleaner.clean(standard_data)

# 4. 데이터 검증
validator = DocumentValidator()
success, model = validator.validate(cleaned_data)

if success:
    print("✅ 검증 성공!")
    
    # 5. 저장
    with open("data/processed/statutes/statute-347.json", "w", encoding="utf-8") as f:
        json.dump(model.model_dump(), f, ensure_ascii=False, indent=2)
    
    print("✅ 저장 완료!")
else:
    print("❌ 검증 실패:")
    for error in validator.get_errors():
        print(f"   - {error}")
```

---

## 자주 묻는 질문

### Q1: 전처리를 안 하면 어떻게 되나요?

**A:** 여러 문제가 발생할 수 있습니다:

- ❌ **검색이 안 됨**: 공백이나 특수문자 때문에 검색어를 찾지 못함
- ❌ **AI가 이해 못함**: 형식이 일관되지 않아서 AI가 혼란스러워함
- ❌ **에러 발생**: 필수 정보가 없어서 프로그램이 중단됨
- ❌ **느린 처리**: 불필요한 데이터가 많아서 처리 속도가 느려짐

**예시:**
```
전처리 전: "  형법 제347조  "  ← 검색어 "형법 제347조"를 찾지 못함
전처리 후: "형법 제347조"      ← 검색어를 정확히 찾음 ✅
```

---

### Q2: 전처리는 한 번만 하면 되나요?

**A:** 상황에 따라 다릅니다:

- ✅ **원본 데이터가 변경되지 않으면**: 한 번만 하면 됨
- ✅ **새로운 데이터를 추가하면**: 새로 추가된 데이터만 전처리
- ✅ **원본 데이터를 수정하면**: 수정된 데이터만 다시 전처리

**권장 사항:**
- 원본 데이터는 절대 수정하지 말고 보존
- 전처리된 데이터만 사용
- 문제 발생 시 원본에서 다시 전처리

---

### Q3: 전처리 중 에러가 발생하면?

**A:** 에러 메시지를 확인하고 수정하세요:

**에러 예시:**
```
❌ 검증 실패: 'type' 필드가 없습니다.
```

**해결 방법:**
1. 에러 메시지 확인
2. 원본 데이터 파일 열기
3. 누락된 필드 추가
4. 다시 전처리 실행

**예시:**
```json
// 에러 발생 데이터
{
  "id": "statute-347",
  // "type" 필드가 없음!
  "title": "형법 제347조"
}

// 수정 후
{
  "id": "statute-347",
  "type": "statute",  // ← 추가!
  "title": "형법 제347조"
}
```

---

### Q4: 전처리 시간이 얼마나 걸리나요?

**A:** 데이터 양에 따라 다릅니다:

- 📄 **소규모 (10개 파일)**: 약 1-2초
- 📚 **중규모 (100개 파일)**: 약 10-30초
- 📖 **대규모 (1000개 파일)**: 약 2-5분

**빠르게 하려면:**
- 전처리와 인덱싱을 분리해서 실행
- 필요한 데이터만 선택해서 처리
- 병렬 처리 사용 (고급)

---

### Q5: 전처리된 데이터를 수정해도 되나요?

**A:** 가능하지만 권장하지 않습니다:

**권장하지 않는 이유:**
- 원본 데이터와 불일치 발생
- 나중에 다시 전처리하면 수정 내용이 사라짐
- 문제 추적이 어려워짐

**권장 방법:**
1. 원본 데이터 수정
2. 다시 전처리 실행
3. 전처리된 데이터 사용

---

### Q6: 전처리 규칙을 바꾸고 싶어요

**A:** `DataCleaner` 클래스를 수정하거나 상속하세요:

**예시:**
```python
from src.processors.cleaner import DataCleaner

class CustomDataCleaner(DataCleaner):
    """커스텀 정제 규칙 추가"""
    
    def _custom_rule(self, data):
        """새로운 정제 규칙"""
        # 예: 특정 키워드 제거
        if "content" in data:
            data["content"] = data["content"].replace("불필요한 키워드", "")
        return data
    
    def clean(self, data, rules=None):
        """기본 정제 + 커스텀 정제"""
        # 기본 정제 수행
        cleaned = super().clean(data, rules)
        # 커스텀 정제 수행
        cleaned = self._custom_rule(cleaned)
        return cleaned

# 사용
custom_cleaner = CustomDataCleaner()
cleaned_data = custom_cleaner.clean(data)
```

---

## 요약

### 데이터 전처리 = 요리 재료 손질하기 🍳

1. **형식 변환**: 모든 재료를 같은 그릇에 담기
2. **데이터 정제**: 불필요한 부분 제거, 깨끗이 정리
3. **데이터 검증**: 필요한 재료가 모두 있는지 확인
4. **중복 제거**: 같은 재료가 여러 개 있으면 하나만 남기기
5. **최종 저장**: 정리된 재료를 깨끗한 곳에 보관

### 핵심 포인트

- ✅ **전처리는 필수**: AI가 제대로 작동하려면 깨끗한 데이터가 필요
- ✅ **원본 보존**: 원본 데이터는 절대 수정하지 말고 보존
- ✅ **단계별 확인**: 각 단계마다 결과를 확인하며 진행
- ✅ **에러 처리**: 에러 발생 시 메시지를 확인하고 수정

### 다음 단계

전처리가 완료되면:
1. ✅ 데이터 검증 확인
2. ✅ 벡터 DB 인덱싱
3. ✅ 검색 테스트
4. ✅ AI 질의응답 테스트

---

**더 자세한 내용은 다음 문서를 참고하세요:**
- [DocumentValidator 사용 가이드](./DOCUMENT_VALIDATOR_GUIDE.md)
- [RAG 데이터 처리 가이드](./RAG_DATA_PROCESSING_GUIDE.md)
- [RAG 데이터 구축 가이드](./RAG_DATA_BUILD_GUIDE.md)

---

**질문이나 문제가 있으면 GitHub Issues에 문의해주세요!** 💬

