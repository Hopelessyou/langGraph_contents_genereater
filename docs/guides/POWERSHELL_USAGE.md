# PowerShell 사용 가이드

PowerShell에서 데이터 전처리 스크립트를 실행하는 방법입니다.

---

## 문제: 백슬래시(`\`) 줄바꿈 에러

PowerShell에서는 **백슬래시(`\`)**로 줄바꿈을 할 수 없습니다!

### ❌ 잘못된 방법 (에러 발생)

```powershell
python scripts/process_and_index.py \
    --input-dir "data/collected/cases" \
    --doc-type "case"
```

**에러 메시지:**
```
단항 연산자 '--' 뒤에 식이 없습니다.
```

---

## ✅ 올바른 방법

### 방법 1: 백틱(`` ` ``) 사용 (권장)

PowerShell에서는 **백틱(`` ` ``)**을 사용하여 줄바꿈을 합니다.

```powershell
python scripts/process_and_index.py `
    --input-dir "data/collected/cases" `
    --doc-type "case"
```

**주의사항:**
- 백틱(`` ` ``)은 각 줄의 **끝**에 있어야 합니다
- 백틱 뒤에 공백이 있으면 안 됩니다

### 방법 2: 한 줄로 작성

```powershell
python scripts/process_and_index.py --input-dir "data/collected/cases" --doc-type "case"
```

### 방법 3: 세미콜론(`;`) 사용

```powershell
python scripts/process_and_index.py --input-dir "data/collected/cases"; --doc-type "case"
```

**주의:** 세미콜론은 명령어를 분리하므로 이 방법은 작동하지 않습니다. 방법 1 또는 2를 사용하세요.

---

## 실제 사용 예시

### 법령 데이터 전처리

```powershell
# 방법 1: 백틱 사용
python scripts/process_and_index.py `
    --input-dir "data/collected/statutes" `
    --doc-type "statute"

# 방법 2: 한 줄로
python scripts/process_and_index.py --input-dir "data/collected/statutes" --doc-type "statute"
```

### 판례 데이터 전처리

```powershell
# 방법 1: 백틱 사용
python scripts/process_and_index.py `
    --input-dir "data/collected/cases" `
    --doc-type "case"

# 방법 2: 한 줄로
python scripts/process_and_index.py --input-dir "data/collected/cases" --doc-type "case"
```

### 옵션 포함 예시

```powershell
# 전처리만 수행 (인덱싱 건너뛰기)
python scripts/process_and_index.py `
    --input-dir "data/collected/statutes" `
    --doc-type "statute" `
    --skip-index

# 출력 디렉토리 지정
python scripts/process_and_index.py `
    --input-dir "data/collected/statutes" `
    --output-dir "data/processed/statutes" `
    --doc-type "statute"
```

---

## 자주 발생하는 오류

### 오류 1: "단항 연산자 '--' 뒤에 식이 없습니다"

**원인:** 백슬래시(`\`)를 사용했거나 백틱 위치가 잘못됨

**해결:**
```powershell
# ❌ 잘못된 방법
python scripts/process_and_index.py \
    --input-dir "data/collected/cases"

# ✅ 올바른 방법
python scripts/process_and_index.py `
    --input-dir "data/collected/cases"
```

### 오류 2: "식 또는 문에서 예기치 않은 토큰입니다"

**원인:** 백틱 뒤에 공백이 있거나 줄바꿈이 잘못됨

**해결:**
```powershell
# ❌ 잘못된 방법 (백틱 뒤에 공백)
python scripts/process_and_index.py ` 
    --input-dir "data/collected/cases"

# ✅ 올바른 방법 (백틱 뒤에 바로 줄바꿈)
python scripts/process_and_index.py `
    --input-dir "data/collected/cases"
```

### 오류 3: "디렉토리를 찾을 수 없습니다"

**원인:** 경로가 잘못되었거나 디렉토리가 없음

**해결:**
```powershell
# 디렉토리 확인
Get-ChildItem "data/collected"

# 올바른 경로 사용
python scripts/process_and_index.py --input-dir "data/collected/cases" --doc-type "case"
```

---

## PowerShell vs Bash 비교

| 작업 | Bash (Linux/Mac) | PowerShell (Windows) |
|------|-----------------|---------------------|
| 줄바꿈 | `\` (백슬래시) | `` ` `` (백틱) |
| 경로 구분자 | `/` | `/` 또는 `\` |
| 문자열 따옴표 | `"` 또는 `'` | `"` 또는 `'` |

### Bash 예시
```bash
python scripts/process_and_index.py \
    --input-dir "data/collected/cases" \
    --doc-type "case"
```

### PowerShell 예시
```powershell
python scripts/process_and_index.py `
    --input-dir "data/collected/cases" `
    --doc-type "case"
```

---

## 편리한 팁

### 팁 1: PowerShell 스크립트 파일 사용

복잡한 명령어는 `.ps1` 파일로 저장하여 사용:

```powershell
# preprocess.ps1 파일 생성
python scripts/process_and_index.py `
    --input-dir "data/collected/statutes" `
    --doc-type "statute"

# 실행
.\preprocess.ps1
```

### 팁 2: 변수 사용

```powershell
$inputDir = "data/collected/statutes"
$docType = "statute"

python scripts/process_and_index.py --input-dir $inputDir --doc-type $docType
```

### 팁 3: 함수로 만들기

```powershell
function Preprocess-Data {
    param(
        [string]$InputDir,
        [string]$DocType
    )
    
    python scripts/process_and_index.py --input-dir $InputDir --doc-type $DocType
}

# 사용
Preprocess-Data -InputDir "data/collected/statutes" -DocType "statute"
```

---

## 빠른 참조

### 가장 간단한 방법 (한 줄)

```powershell
python scripts/process_and_index.py --input-dir "data/collected/cases" --doc-type "case"
```

### 여러 옵션 사용 (백틱 사용)

```powershell
python scripts/process_and_index.py `
    --input-dir "data/collected/cases" `
    --output-dir "data/processed/cases" `
    --doc-type "case" `
    --skip-index
```

---

**더 자세한 내용은 다음 문서를 참고하세요:**
- [데이터 전처리 코드 예시](./DATA_PREPROCESSING_CODE_EXAMPLES.md)
- [데이터 전처리 쉽게 이해하기](./DATA_PREPROCESSING_EASY_GUIDE.md)

