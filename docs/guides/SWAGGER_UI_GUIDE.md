# Swagger UI 사용 가이드

IBS 법률 AI 시스템의 Swagger UI를 활용하여 API를 테스트하고 사용하는 방법을 상세히 설명합니다.

---

## 📍 접속 방법

### 1. 서버 실행 확인

먼저 FastAPI 서버가 실행 중인지 확인합니다:

```powershell
# 서버 실행 (아직 실행하지 않았다면)
python -m src.api.main
```

서버가 정상적으로 실행되면 다음과 같은 메시지가 표시됩니다:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. 브라우저 접속

서버가 실행 중이면 브라우저에서 다음 주소로 접속합니다:

```
http://localhost:8000/docs
```

**참고**: 
- 기본 포트는 `8000`입니다. `config/settings.py`에서 `API_PORT`로 변경 가능합니다.
- 로컬 네트워크의 다른 기기에서 접속하려면 `API_HOST=0.0.0.0`으로 설정해야 합니다.

---

## 🎯 화면 구성 상세 설명

Swagger UI 화면은 직관적이고 사용하기 쉽게 구성되어 있습니다.

### 상단 헤더 영역

#### API 정보 섹션
- **제목**: "IBS 법률 AI 시스템 API"
- **설명**: "법률 정보 RAG 기반 질의응답 API"
- **버전**: 현재 API 버전 (예: "0.1.0")
- **서버 URL**: 기본 서버 주소 (예: `http://localhost:8000`)

#### Authorize 버튼 (🔒)
- **위치**: 상단 오른쪽
- **용도**: API 키 인증이 필요한 엔드포인트에 사용
- **사용 방법**:
  1. 버튼 클릭
  2. 팝업 창에 API 키 입력
  3. "Authorize" 클릭
  4. 인증이 완료되면 🔒 아이콘이 채워진 상태로 변경됨

**주의**: 
- API 키는 환경 변수 `API_KEY`에 설정되어 있어야 합니다.
- 관리자 엔드포인트(`/api/v1/admin/*`)는 API 키가 필수입니다.
- 일반 검색/질의응답 엔드포인트는 API 키가 필요 없습니다.

### 왼쪽 사이드바 (엔드포인트 목록)

엔드포인트는 기능별로 그룹화되어 있습니다:

#### 1. `health` - 헬스체크
- `GET /api/v1/health`: 기본 서버 상태 확인
- `GET /api/v1/health/detailed`: 상세 시스템 상태 확인

#### 2. `search` - 문서 검색
- `GET /api/v1/search`: GET 방식 검색 (쿼리 파라미터 사용)
- `POST /api/v1/search`: POST 방식 검색 (JSON 본문 사용)

#### 3. `ask` - 질의응답
- `POST /api/v1/ask`: 일반 질의응답 (비스트리밍)
- `POST /api/v1/ask/stream`: 스트리밍 질의응답 (실시간 응답)

#### 4. `generate` - 콘텐츠 생성
- `POST /api/v1/generate`: 법률 콘텐츠 생성 (블로그, 기사 등)

#### 5. `admin` - 관리자 기능 (🔒 API 키 필요)
- `POST /api/v1/admin/index`: 디렉토리 인덱싱
- `POST /api/v1/admin/index/incremental`: 증분 인덱싱
- `GET /api/v1/admin/index/status`: 인덱스 상태 조회
- `POST /api/v1/admin/index/reset`: 인덱스 초기화
- `POST /api/v1/admin/upload`: 파일 업로드 및 인덱싱

#### 6. `monitoring` - 모니터링
- `GET /api/v1/monitoring/stats`: API 통계 조회
- `GET /api/v1/monitoring/vector-db`: 벡터 DB 상태 조회 (🔒 API 키 필요)

### 메인 영역 (엔드포인트 상세)

엔드포인트를 클릭하면 다음 정보가 표시됩니다:

#### 1. 엔드포인트 설명
- **용도**: 해당 엔드포인트의 목적과 기능
- **HTTP 메서드**: GET, POST 등
- **경로**: `/api/v1/...`

#### 2. Parameters 섹션
- **Query Parameters** (GET 요청): URL 쿼리 스트링 파라미터
- **Request Body** (POST 요청): JSON 형식의 요청 본문
- **Required 표시**: 빨간색 별표(*)가 있는 필드는 필수입니다
- **타입 표시**: 각 필드의 데이터 타입 (string, integer, array 등)
- **기본값**: 필드에 기본값이 있으면 표시됩니다
- **설명**: 각 필드의 용도와 사용법

#### 3. Responses 섹션
- **200**: 성공 응답 예시
- **400**: 잘못된 요청 (Validation Error)
- **401**: 인증 실패
- **422**: 요청 본문 검증 실패
- **500**: 서버 내부 오류

#### 4. Schema 섹션
- **Request Schema**: 요청 데이터 구조 상세 설명
- **Response Schema**: 응답 데이터 구조 상세 설명
- 각 필드의 타입, 제약 조건, 설명 등이 포함됩니다

#### 5. "Try it out" 버튼
- 클릭하면 파라미터 입력 폼이 활성화됩니다
- 요청을 실제로 서버에 전송할 수 있습니다

---

## 🚀 사용 방법 (단계별 상세 가이드)

### 예제 1: 헬스체크 테스트

#### 기본 헬스체크 (`GET /api/v1/health`)

**목적**: 서버가 정상적으로 실행 중인지 빠르게 확인

**단계별 사용법:**

1. **엔드포인트 찾기**
   - 왼쪽 사이드바에서 `health` 섹션을 클릭하여 확장
   - `GET /api/v1/health` 엔드포인트 클릭

2. **엔드포인트 상세 정보 확인**
   - **Description**: "헬스체크" - 서버 상태 확인용
   - **Parameters**: 없음 (파라미터가 필요 없는 간단한 엔드포인트)
   - **Responses**: 
     - `200`: 성공 응답
     - `500`: 서버 오류

3. **"Try it out" 버튼 클릭**
   - 파라미터 입력 폼이 활성화됩니다
   - 이 엔드포인트는 파라미터가 없으므로 바로 실행 가능합니다

4. **"Execute" 버튼 클릭**
   - 서버로 요청이 전송됩니다
   - 응답이 표시될 때까지 잠시 기다립니다

5. **결과 확인**

   **Response Code**: `200` (성공)
   
   **Response body** (JSON):
   ```json
   {
     "status": "healthy",
     "version": "0.1.0",
     "timestamp": "2025-12-09T14:20:55.404392"
   }
   ```
   
   **응답 필드 설명**:
   - `status`: 서버 상태 (`"healthy"` = 정상)
   - `version`: API 버전
   - `timestamp`: 응답 생성 시간 (ISO 8601 형식)
   
   **Response headers**:
   ```
   content-type: application/json
   content-length: 82
   date: Tue, 09 Dec 2025 05:20:54 GMT
   server: uvicorn
   x-process-time: 0.002544403076171875
   x-ratelimit-limit: 100
   x-ratelimit-remaining: 98
   x-ratelimit-reset: 1765257715
   ```
   
   **헤더 설명**:
   - `x-process-time`: 요청 처리 시간 (초)
   - `x-ratelimit-limit`: 분당 허용 요청 수
   - `x-ratelimit-remaining`: 남은 요청 수
   - `x-ratelimit-reset`: 제한 리셋 시간 (Unix timestamp)
   
   **Curl 명령어**:
   ```bash
   curl -X 'GET' \
     'http://localhost:8000/api/v1/health' \
     -H 'accept: application/json'
   ```
   
   **Request URL**: `http://localhost:8000/api/v1/health`

#### 상세 헬스체크 (`GET /api/v1/health/detailed`)

**목적**: 각 컴포넌트(벡터 DB, 임베딩 모델 등)의 상태를 상세히 확인

**응답 예시:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-12-09T14:20:55.404392",
  "components": {
    "vector_db": {
      "status": "healthy",
      "document_count": 821
    },
    "embedding": {
      "status": "healthy",
      "model": "text-embedding-3-large"
    }
  }
}
```

**응답 필드 설명**:
- `status`: 전체 시스템 상태
  - `"healthy"`: 모든 컴포넌트 정상
  - `"degraded"`: 일부 컴포넌트 문제 있음
- `components.vector_db.status`: 벡터 DB 상태
- `components.vector_db.document_count`: 인덱싱된 문서(청크) 수
- `components.embedding.status`: 임베딩 모델 상태
- `components.embedding.model`: 사용 중인 임베딩 모델명

**문제 해결**:
- `vector_db.status`가 `"unhealthy"`인 경우: 벡터 DB 연결 확인, 데이터 인덱싱 확인
- `embedding.status`가 `"unhealthy"`인 경우: OpenAI API 키 확인, 네트워크 연결 확인

---

### 예제 2: 문서 검색 API 사용

#### POST 방식 검색 (`POST /api/v1/search`)

**목적**: 벡터 검색을 통해 관련 법률 문서를 검색

**단계별 사용법:**

1. **엔드포인트 선택**
   - 왼쪽 사이드바에서 `search` 섹션 확장
   - `POST /api/v1/search` 클릭

2. **"Try it out" 버튼 클릭**
   - Request body 입력 폼이 활성화됩니다

3. **요청 본문 입력**

   **기본 예시 (최소 필수 필드만):**
   ```json
   {
     "query": "사기죄 처벌"
   }
   ```
   - `query`만 입력하면 기본값(`n_results=5`)으로 검색됩니다
   
   **표준 예시:**
   ```json
   {
     "query": "사기죄 처벌",
     "n_results": 5
   }
   ```
   
   **고급 예시 (모든 필터 사용):**
   ```json
   {
     "query": "사기죄 처벌",
     "n_results": 10,
     "document_types": ["statute", "case"],
     "category": "형사",
     "sub_category": "사기"
   }
   ```

4. **필드 상세 설명**

   | 필드 | 타입 | 필수 | 기본값 | 설명 | 제약 조건 |
   |------|------|------|--------|------|----------|
   | `query` | string | ✅ | - | 검색할 키워드 또는 질문 | 최소 1자 이상 |
   | `n_results` | integer | ❌ | 5 | 반환할 결과 수 | 1~20 사이 |
   | `document_types` | array[string] | ❌ | null | 문서 타입 필터 | `["statute", "case", "procedure", "template", "manual", "faq"]` 중 선택 |
   | `category` | string | ❌ | null | 카테고리 필터 | 예: `"형사"`, `"민사"` |
   | `sub_category` | string | ❌ | null | 하위 카테고리 필터 | 예: `"사기"`, `"절도"` |

   **필드별 상세 설명**:
   
   - **`query`**: 
     - 검색할 키워드나 질문을 입력합니다
     - 예: `"사기죄 처벌"`, `"형법 제347조"`, `"사기 판례"`
     - 자연어 질문도 가능합니다: `"사기죄는 어떤 처벌을 받나요?"`
   
   - **`n_results`**:
     - 반환할 검색 결과의 최대 개수입니다
     - 값이 클수록 더 많은 결과를 받지만 응답 시간이 길어질 수 있습니다
     - 권장값: 5~10개
   
   - **`document_types`**:
     - 검색할 문서 타입을 배열로 지정합니다
     - `["statute"]`: 법령만 검색
     - `["case"]`: 판례만 검색
     - `["statute", "case"]`: 법령과 판례 모두 검색
     - 지정하지 않으면 모든 타입 검색
   
   - **`category`**:
     - 법률 카테고리로 필터링합니다
     - 예: `"형사"`, `"민사"`, `"행정"` 등
     - 메타데이터에 `category` 필드가 있는 문서만 검색됩니다
   
   - **`sub_category`**:
     - 세부 카테고리로 필터링합니다
     - 예: `"사기"`, `"절도"`, `"살인"` 등
     - `category`와 함께 사용하면 더 정확한 필터링이 가능합니다

5. **"Execute" 버튼 클릭**

6. **결과 확인**

   **성공 응답 (200)**:
   ```json
   {
     "query": "사기죄 처벌",
     "results": [
       {
         "id": "case-2010도2810_chunk_1",
         "document": "【판결 요지】 을 수긍한 사례. [3] 계(契) 운영을 통한 甲의 사기범행을 미필적으로나마 인식 또는 예견하면서도 그 범행의 실행행위를 직·간접적으로 도와 용이하게 한 乙의 행위가 사기방조죄에 해당한다고 한 원심판단을 수긍한 사례",
         "metadata": {
           "type": "case",
           "document_type": "case",
           "title": "대법원 2010도2810 판결 (청크 2)",
           "case_number": "2010도2810",
           "court": "대법원",
           "category": "형사",
           "sub_category": "사기",
           "year": 2010,
           "keywords": "사기",
           "section_title": "판결 요지",
           "section_type": "overview",
           "holding": "을 수긍한 사례. [3] 계(契) 운영을 통한 甲의 사기범행을 미필적으로나마 인식 또는 예견하면서도 그 범행의 실행행위를 직·간접적으로 도와 용이하게 한 乙의 행위가 사기방조죄에 해당한다고 한 원심판단을 수긍한 사례",
           "chunk_index": 1,
           "document_id": "case-2010도2810",
           "updated_at": "2025-12-09"
         },
         "distance": 1.348702311515808,
         "score": 0.4258
       }
     ],
     "total": 5,
     "timestamp": "2025-12-09T14:20:55.404392"
   }
   ```
   
   **응답 필드 상세 설명**:
   
   - **`query`**: 검색에 사용된 원본 쿼리
   
   - **`results`**: 검색 결과 배열 (유사도 순으로 정렬)
     - **`id`**: 문서 청크의 고유 ID
     - **`document`**: 문서 내용 (청크)
     - **`metadata`**: 문서 메타데이터
       - `type`: 문서 타입 (`"case"`, `"statute"` 등)
       - `title`: 문서 제목
       - `case_number`: 판례 사건번호 (판례인 경우)
       - `court`: 법원명 (판례인 경우)
       - `category`: 카테고리
       - `sub_category`: 하위 카테고리
       - `year`: 연도
       - `keywords`: 키워드 목록
       - `section_title`: 섹션 제목 (판례의 경우 "판결 요지", "사건 개요" 등)
       - `chunk_index`: 청크 인덱스 (같은 문서 내에서의 순서)
     - **`distance`**: 벡터 거리 (작을수록 유사함, 0에 가까울수록 좋음)
     - **`score`**: 유사도 점수 (0~1, 클수록 유사함, `1 / (1 + distance)`로 계산)
   
   - **`total`**: 반환된 결과 수
   
   - **`timestamp`**: 응답 생성 시간

   **에러 응답 (400 - Validation Error)**:
   ```json
   {
     "detail": [
       {
         "loc": ["body", "query"],
         "msg": "field required",
         "type": "value_error.missing"
       }
     ]
   }
   ```
   - `query` 필드가 누락된 경우
   
   **에러 응답 (422 - Unprocessable Entity)**:
   ```json
   {
     "detail": [
       {
         "loc": ["body", "n_results"],
         "msg": "ensure this value is less than or equal to 20",
         "type": "value_error.number.not_le",
         "ctx": {"limit_value": 20}
       }
     ]
   }
   ```
   - `n_results`가 20을 초과한 경우

#### GET 방식 검색 (`GET /api/v1/search`)

**목적**: URL 쿼리 파라미터를 사용한 간단한 검색

**사용법:**

1. `GET /api/v1/search` 엔드포인트 선택

2. "Try it out" 클릭

3. **Query Parameters 입력**:
   - `query`: 검색어 (필수)
   - `n_results`: 결과 수 (선택, 기본값: 5)
   - `document_types`: 문서 타입, 쉼표로 구분 (예: `"statute,case"`)
   - `category`: 카테고리 (선택)
   - `sub_category`: 하위 카테고리 (선택)

4. "Execute" 클릭

**예시 URL**:
```
http://localhost:8000/api/v1/search?query=사기&n_results=5&document_types=statute,case&category=형사&sub_category=사기
```

**GET vs POST 차이점**:
- **GET**: URL에 파라미터가 노출되므로 브라우저에서 쉽게 테스트 가능, 캐싱 가능
- **POST**: 복잡한 JSON 구조 전송 가능, 보안상 더 안전 (URL에 노출되지 않음)
- **권장**: 일반적으로 POST 방식을 권장합니다 (더 유연하고 안전함)

---

### 예제 3: 질의응답 API 사용

#### 일반 질의응답 (`POST /api/v1/ask`)

**목적**: 사용자의 법률 질문에 대해 RAG 기반으로 AI 답변 생성

**단계별 사용법:**

1. **엔드포인트 선택**
   - 왼쪽 사이드바에서 `ask` 섹션 확장
   - `POST /api/v1/ask` 클릭

2. **"Try it out" 버튼 클릭**

3. **요청 본문 입력**

   **기본 예시:**
   ```json
   {
     "query": "사기죄는 어떤 처벌을 받나요?"
   }
   ```
   
   **세션을 사용한 연속 대화 예시:**
   ```json
   {
     "query": "사기죄는 어떤 처벌을 받나요?",
     "session_id": "my-session-001",
     "document_types": ["statute", "case"]
   }
   ```

4. **필드 상세 설명**

   | 필드 | 타입 | 필수 | 기본값 | 설명 |
   |------|------|------|--------|------|
   | `query` | string | ✅ | - | 질문 내용 |
   | `session_id` | string | ❌ | null | 세션 ID (대화 연속성 유지) |
   | `stream` | boolean | ❌ | false | 스트리밍 응답 여부 (이 엔드포인트에서는 false만 사용) |
   | `document_types` | array[string] | ❌ | null | 검색할 문서 타입 |

   **필드별 상세 설명**:
   
   - **`query`**: 
     - 사용자의 질문을 입력합니다
     - 자연어 질문이 가능합니다
     - 예: `"사기죄는 어떤 처벌을 받나요?"`, `"형법 제347조의 내용은?"`
   
   - **`session_id`**:
     - 대화 연속성을 유지하기 위한 세션 ID입니다
     - 같은 `session_id`를 사용하면 이전 대화 맥락을 기억합니다
     - 지정하지 않으면 자동으로 생성됩니다
     - 응답에 `session_id`가 포함되므로 저장해두고 다음 요청에 사용하세요
     - 세션은 기본적으로 30분간 유지됩니다 (설정 가능)
   
   - **`stream`**:
     - `false`: 전체 응답을 한 번에 받습니다 (이 엔드포인트)
     - `true`: 스트리밍 응답을 원하면 `/api/v1/ask/stream` 엔드포인트 사용
   
   - **`document_types`**:
     - 검색할 문서 타입을 지정합니다
     - 지정하지 않으면 모든 타입에서 검색합니다

5. **"Execute" 버튼 클릭**

6. **결과 확인**

   **성공 응답 (200)**:
   ```json
   {
     "query": "사기죄는 어떤 처벌을 받나요?",
     "response": "사기죄는 형법 제347조에 규정되어 있으며, 10년 이하의 징역 또는 2천만원 이하의 벌금에 처해집니다. 구체적인 처벌은 피해액, 범행 방법, 재범 여부 등에 따라 달라질 수 있습니다.\n\n관련 법령:\n- 형법 제347조(사기)\n\n관련 판례:\n- 대법원 2010도2810 판결: 사기방조죄에 대한 판단 기준",
     "session_id": "550e8400-e29b-41d4-a716-446655440000",
     "sources": [
       {
         "id": "case-2010도2810_chunk_1",
         "title": "대법원 2010도2810 판결 (청크 2)",
         "type": "case"
       },
       {
         "id": "statute-형법-347",
         "title": "형법 제347조",
         "type": "statute"
       }
     ],
     "timestamp": "2025-12-09T14:25:30.123456"
   }
   ```
   
   **응답 필드 상세 설명**:
   
   - **`query`**: 사용자가 입력한 원본 질문
   
   - **`response`**: AI가 생성한 답변
     - 관련 법령과 판례를 참고하여 생성됩니다
     - 법령 조문 번호와 판례 번호가 포함됩니다
     - 실용적인 조언이 포함될 수 있습니다
   
   - **`session_id`**: 세션 ID
     - 다음 질문에서 이 값을 사용하면 대화 맥락이 유지됩니다
     - 자동 생성된 경우 이 값을 저장해두세요
   
   - **`sources`**: 답변 생성에 참고한 문서 목록
     - 최대 3개까지 표시됩니다 (설정 가능)
     - 각 항목은 `id`, `title`, `type`을 포함합니다
     - 클릭하면 해당 문서를 확인할 수 있습니다
   
   - **`timestamp`**: 응답 생성 시간

#### 스트리밍 질의응답 (`POST /api/v1/ask/stream`)

**목적**: 실시간으로 스트리밍 응답을 받아 사용자 경험 향상

**특징**:
- 응답이 생성되는 대로 실시간으로 전송됩니다
- 긴 답변의 경우 사용자가 기다리는 시간을 줄일 수 있습니다
- Server-Sent Events (SSE) 형식으로 전송됩니다

**사용법:**

1. `POST /api/v1/ask/stream` 엔드포인트 선택

2. "Try it out" 클릭

3. **요청 본문 입력**:
   ```json
   {
     "query": "사기죄는 어떤 처벌을 받나요?",
     "session_id": "my-session-001"
   }
   ```

4. "Execute" 클릭

5. **스트리밍 응답 확인**

   **응답 형식** (Server-Sent Events):
   ```
   data: {"chunk": "사기죄는"}
   
   data: {"chunk": " 형법 제347조에"}
   
   data: {"chunk": " 규정되어 있으며,"}
   
   data: {"chunk": " 10년 이하의"}
   
   data: {"chunk": " 징역 또는"}
   
   data: {"chunk": " 2천만원 이하의"}
   
   data: {"chunk": " 벌금에"}
   
   data: {"chunk": " 처해집니다."}
   
   data: {"done": true, "full_response": "사기죄는 형법 제347조에 규정되어 있으며, 10년 이하의 징역 또는 2천만원 이하의 벌금에 처해집니다."}
   ```

   **스트리밍 응답 처리**:
   - 각 `data:` 라인은 JSON 형식의 이벤트입니다
   - `chunk`: 실시간으로 전송되는 텍스트 조각
   - `done`: 스트리밍 완료 여부
   - `full_response`: 전체 응답 (완료 시)

   **주의사항**:
   - Swagger UI에서는 스트리밍 응답이 한 번에 표시될 수 있습니다
   - 실제 애플리케이션에서는 EventSource API나 fetch API를 사용하여 실시간으로 처리합니다
   - JavaScript 예시:
     ```javascript
     const eventSource = new EventSource('/api/v1/ask/stream', {
       method: 'POST',
       body: JSON.stringify({query: "사기죄는?"})
     });
     
     eventSource.onmessage = (event) => {
       const data = JSON.parse(event.data);
       if (data.chunk) {
         // 실시간으로 텍스트 표시
         console.log(data.chunk);
       }
       if (data.done) {
         eventSource.close();
       }
     };
     ```

**연속 대화 예시:**

1. **첫 번째 질문**:
   ```json
   {
     "query": "사기죄는 무엇인가요?",
     "session_id": "my-session-001"
   }
   ```
   응답에서 `session_id` 확인: `"my-session-001"`

2. **두 번째 질문** (같은 세션):
   ```json
   {
     "query": "그럼 처벌은 어떻게 되나요?",
     "session_id": "my-session-001"
   }
   ```
   - AI는 이전 대화에서 "사기죄"에 대해 언급했다는 것을 기억합니다
   - "그럼"이라는 대명사가 무엇을 가리키는지 이해합니다

3. **세 번째 질문** (계속):
   ```json
   {
     "query": "판례에서 중요한 기준은?",
     "session_id": "my-session-001"
   }
   ```
   - "사기죄"의 "판례"를 의미한다는 것을 이해합니다

---

### 예제 4: 콘텐츠 생성 API 사용 (`POST /api/v1/generate`)

**목적**: 법률 관련 콘텐츠(블로그, 기사, 의견서 등)를 자동 생성

**단계별 사용법:**

1. **엔드포인트 선택**
   - `generate` 섹션에서 `POST /api/v1/generate` 클릭

2. **"Try it out" 버튼 클릭**

3. **요청 본문 입력**

   **기본 예시 (블로그 포스팅):**
   ```json
   {
     "topic": "사기죄 처벌과 대응방법",
     "content_type": "blog"
   }
   ```
   
   **고급 예시 (의견서):**
   ```json
   {
     "topic": "특정경제범죄 가중처벌법 위반 사건",
     "content_type": "opinion",
     "style": "전문적",
     "target_length": 3000,
     "include_sections": ["법적기준", "판례", "대응방법"],
     "keywords": ["사기", "가중처벌", "형법"],
     "document_types": ["statute", "case"],
     "n_references": 10
   }
   ```

4. **필드 상세 설명**

   | 필드 | 타입 | 필수 | 기본값 | 설명 |
   |------|------|------|--------|------|
   | `topic` | string | ✅ | - | 생성할 콘텐츠 주제/키워드 |
   | `content_type` | string | ❌ | "blog" | 콘텐츠 타입: `"blog"`, `"article"`, `"opinion"`, `"analysis"`, `"faq"` |
   | `style` | string | ❌ | null | 작성 스타일 (예: `"전문적"`, `"대중적"`, `"간결한"`) |
   | `target_length` | integer | ❌ | null | 목표 글자 수 (공백 제외) |
   | `include_sections` | array[string] | ❌ | null | 포함할 섹션 목록 |
   | `keywords` | array[string] | ❌ | null | 반드시 포함할 키워드 목록 |
   | `document_types` | array[string] | ❌ | null | 참고할 문서 타입 |
   | `n_references` | integer | ❌ | 5 | 참고할 문서 수 (1~20) |

   **콘텐츠 타입별 특징**:
   
   - **`blog`**: 
     - 독자 친화적이고 이해하기 쉬운 문체
     - 법률 용어는 쉬운 설명과 함께 사용
     - 실제 사례와 판례 활용
     - 실용적인 조언 포함
   
   - **`article`**:
     - 객관적이고 중립적인 톤
     - 사실에 기반한 정확한 정보
     - 법령 조문과 판례 명확히 인용
     - 전문가 의견과 분석 포함
   
   - **`opinion`**:
     - 전문적이고 정확한 법률 분석
     - 관련 법령과 판례 상세 인용
     - 법리적 논거 체계적 제시
     - 결론과 권고사항 명확히 제시
   
   - **`analysis`**:
     - 사건의 사실관계 명확히 정리
     - 법적 쟁점 체계적 분석
     - 관련 법령과 판례 비교 분석
     - 법리적 판단과 시사점 제시
   
   - **`faq`**:
     - 질문은 일반인이 궁금해할 만한 내용
     - 답변은 간결하고 명확하게
     - 관련 법령 조문 번호 명시
     - 실무적인 조언 포함

5. **"Execute" 버튼 클릭**

6. **결과 확인**

   **성공 응답 (200)**:
   ```json
   {
     "success": true,
     "content": "# 사기죄 처벌과 대응방법\n\n## 1. 도입부\n\n사기죄는 우리 사회에서 가장 흔한 범죄 중 하나입니다...",
     "title": "사기죄 처벌과 대응방법 - 전문가가 알려주는 완벽 가이드",
     "sections": {
       "1. 도입부": "사기죄는 우리 사회에서...",
       "2. 법적 기준과 처벌": "형법 제347조에 따르면...",
       "3. 실제 사례와 판례": "대법원 2010도2810 판결에서는..."
     },
     "references": [
       {
         "title": "형법 제347조",
         "type": "statute",
         "id": "statute-형법-347",
         "relevance": 0.95
       },
       {
         "title": "대법원 2010도2810 판결",
         "type": "case",
         "id": "case-2010도2810_chunk_1",
         "relevance": 0.88
       }
     ],
     "metadata": {
       "content_type": "blog",
       "topic": "사기죄 처벌과 대응방법",
       "word_count": 2847
     },
     "timestamp": "2025-12-09T14:30:00.123456"
   }
   ```

### 예제 5: 파일 업로드 (관리자 API)

**주의**: 이 엔드포인트는 API 키 인증이 필요합니다.

1. **API 키 인증**
   - 상단의 "Authorize" 버튼 클릭
   - 팝업 창에 API 키 입력 (환경 변수 `API_KEY`에 설정된 값)
   - "Authorize" 클릭
   - 🔒 아이콘이 채워진 상태로 변경되면 인증 완료

2. **엔드포인트 선택**
   - `admin` 섹션에서 `POST /api/v1/admin/upload` 클릭

3. **"Try it out" 버튼 클릭**

4. **파일 선택**
   - "Choose File" 버튼 클릭
   - 업로드할 JSON 파일 선택
   - 예: `data/samples/statute-347.json`
   - 또는 `data/processed/statutes/` 폴더의 JSON 파일

5. **"Execute" 버튼 클릭**

6. **결과 확인**

   **성공 응답 (200)**:
   ```json
   {
     "success": true,
     "message": "문서가 성공적으로 인덱싱되었습니다.",
     "document_id": "statute-형법-347",
     "chunks_count": 3
   }
   ```

   **에러 응답 (400)**:
   ```json
   {
     "detail": "유효하지 않은 JSON 파일입니다."
   }
   ```
   - JSON 형식이 올바르지 않은 경우

   **에러 응답 (401)**:
   ```json
   {
     "detail": "API 키가 필요합니다."
   }
   ```
   - API 키가 없거나 잘못된 경우

---

## 💡 유용한 기능들

### 1. 스키마 보기
- 각 엔드포인트의 "Schema" 섹션을 클릭하면
- 요청/응답 데이터 구조를 자세히 볼 수 있습니다
- 필수 필드, 선택 필드, 데이터 타입 등을 확인할 수 있습니다

### 2. 예시 값 사용
- 많은 필드에 "Example" 값이 표시됩니다
- 이를 복사해서 사용하거나 참고할 수 있습니다

### 3. cURL 명령어 복사
- "Execute" 후 "Curl" 섹션에서
- 실제 사용 가능한 curl 명령어를 복사할 수 있습니다
- 터미널에서 바로 사용 가능합니다

### 4. Request URL 확인
- "Execute" 후 "Request URL" 섹션에서
- 실제 요청 URL을 확인할 수 있습니다
- 다른 도구에서 사용할 수 있습니다

---

## 🔍 각 엔드포인트 상세 설명

### Health 엔드포인트

#### `GET /api/v1/health`

**용도**: 서버가 정상적으로 실행 중인지 빠르게 확인

**파라미터**: 없음

**응답 필드**:
- `status`: 서버 상태 (`"healthy"` = 정상)
- `version`: API 버전
- `timestamp`: 응답 생성 시간

**사용 시나리오**:
- 서버 모니터링
- 헬스체크 엔드포인트 (로드밸런서 등)
- 빠른 서버 상태 확인

---

#### `GET /api/v1/health/detailed`

**용도**: 각 컴포넌트의 상세 상태 확인

**파라미터**: 없음

**응답 구조**:
```json
{
  "status": "healthy" | "degraded",
  "version": "0.1.0",
  "timestamp": "2025-12-09T14:20:55.404392",
  "components": {
    "vector_db": {
      "status": "healthy" | "unhealthy",
      "document_count": 821,
      "error": "..."  // unhealthy인 경우
    },
    "embedding": {
      "status": "healthy" | "unhealthy",
      "model": "text-embedding-3-large",
      "error": "..."  // unhealthy인 경우
    }
  }
}
```

**상태 해석**:
- `status: "healthy"`: 모든 컴포넌트 정상
- `status: "degraded"`: 일부 컴포넌트 문제 있음 (서비스는 가능하나 일부 기능 제한)
- `components.vector_db.status: "unhealthy"`: 벡터 DB 연결 실패 또는 데이터 없음
- `components.embedding.status: "unhealthy"`: 임베딩 모델 초기화 실패

**문제 해결**:
- 벡터 DB가 unhealthy인 경우:
  1. `data/vector_db` 폴더 확인
  2. 데이터 인덱싱 여부 확인: `python scripts/check_indexed_data.py`
  3. ChromaDB 설치 확인: `pip install chromadb`
- 임베딩 모델이 unhealthy인 경우:
  1. `OPENAI_API_KEY` 환경 변수 확인
  2. 네트워크 연결 확인
  3. OpenAI API 사용량 확인

---

### Search 엔드포인트

#### `POST /api/v1/search`

**용도**: 벡터 검색을 통해 관련 법률 문서 검색

**요청 본문 구조**:
```json
{
  "query": "검색어 또는 질문",
  "n_results": 5,                    // 1~20 사이
  "document_types": ["statute"],      // 선택 가능
  "category": "형사",                 // 선택 가능
  "sub_category": "사기"              // 선택 가능
}
```

**응답 구조**:
```json
{
  "query": "검색어",
  "results": [
    {
      "id": "문서-청크-ID",
      "document": "문서 내용",
      "metadata": {
        "type": "case" | "statute" | "procedure" | ...,
        "title": "문서 제목",
        "category": "형사",
        "sub_category": "사기",
        // ... 기타 메타데이터
      },
      "distance": 1.35,  // 벡터 거리 (작을수록 유사)
      "score": 0.4258    // 유사도 점수 (0~1, 클수록 유사)
    }
  ],
  "total": 5,
  "timestamp": "2025-12-09T14:20:55.404392"
}
```

**검색 알고리즘**:
1. 쿼리를 임베딩 벡터로 변환
2. 벡터 DB에서 유사한 문서 검색 (코사인 유사도)
3. 메타데이터 필터 적용 (document_types, category, sub_category)
4. 거리 기반 재랭킹
5. 상위 N개 결과 반환

**캐싱 동작**:
- 동일한 쿼리와 필터로 검색하면 캐시된 결과를 반환합니다
- 캐시 TTL: 기본 1시간 (설정 가능)
- 캐시는 메모리에 저장되며 서버 재시작 시 초기화됩니다

**성능 최적화 팁**:
- `n_results`를 필요한 만큼만 설정 (5~10개 권장)
- `document_types` 필터를 사용하여 검색 범위 축소
- `category`, `sub_category` 필터로 더 정확한 결과 얻기

---

#### `GET /api/v1/search`

**용도**: URL 쿼리 파라미터를 사용한 간단한 검색

**Query Parameters**:
- `query` (필수): 검색어
- `n_results` (선택): 결과 수 (기본값: 5)
- `document_types` (선택): 쉼표로 구분 (예: `"statute,case"`)
- `category` (선택): 카테고리
- `sub_category` (선택): 하위 카테고리

**예시 URL**:
```
http://localhost:8000/api/v1/search?query=사기&n_results=5&document_types=statute,case&category=형사
```

**GET vs POST 선택 가이드**:
- **GET 사용 시기**: 
  - 브라우저에서 직접 테스트
  - 간단한 검색
  - URL을 북마크하거나 공유
- **POST 사용 시기**:
  - 복잡한 쿼리
  - 보안이 중요한 경우 (URL에 노출되지 않음)
  - 애플리케이션에서 프로그래밍 방식으로 호출

---

### Ask 엔드포인트

#### `POST /api/v1/ask`

**용도**: 법률 질문에 대해 RAG 기반으로 AI 답변 생성

**요청 본문 구조**:
```json
{
  "query": "질문 내용",
  "session_id": "optional-session-id",
  "stream": false,  // 이 엔드포인트에서는 false만 사용
  "document_types": ["statute", "case"]
}
```

**응답 구조**:
```json
{
  "query": "질문",
  "response": "AI가 생성한 답변",
  "session_id": "세션-ID",
  "sources": [
    {
      "id": "문서-ID",
      "title": "문서 제목",
      "type": "case"
    }
  ],
  "timestamp": "2025-12-09T14:25:30.123456"
}
```

**작동 원리**:
1. 사용자 질문을 임베딩 벡터로 변환
2. 벡터 DB에서 관련 문서 검색
3. 이전 대화 히스토리 가져오기 (session_id가 있는 경우)
4. 검색된 문서와 대화 히스토리를 컨텍스트로 구성
5. LLM에 컨텍스트와 질문을 전달하여 답변 생성
6. 답변과 참조 문서를 반환
7. 대화 히스토리에 저장 (Redis 또는 메모리)

**세션 관리**:
- 세션은 기본적으로 30분간 유지됩니다
- Redis를 사용하면 서버 재시작 후에도 세션 유지 가능
- 세션 타임아웃은 설정에서 변경 가능

**응답 품질 향상 팁**:
- 구체적인 질문을 하면 더 정확한 답변을 받을 수 있습니다
- `document_types`를 지정하여 특정 타입의 문서만 참고하도록 할 수 있습니다
- 연속 대화를 위해 `session_id`를 사용하세요

---

#### `POST /api/v1/ask/stream`

**용도**: 실시간 스트리밍 응답

**특징**:
- Server-Sent Events (SSE) 형식
- 응답이 생성되는 대로 실시간 전송
- 긴 답변의 경우 사용자 대기 시간 감소

**응답 형식**:
```
data: {"chunk": "텍스트 조각"}

data: {"chunk": " 다음 조각"}

data: {"done": true, "full_response": "전체 응답"}
```

**프론트엔드 통합 예시** (JavaScript):
```javascript
async function askQuestionStream(query, sessionId) {
  const response = await fetch('/api/v1/ask/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      session_id: sessionId
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n\n');
    buffer = lines.pop(); // 마지막 불완전한 라인 보관

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        if (data.chunk) {
          // 실시간으로 텍스트 표시
          displayChunk(data.chunk);
        }
        if (data.done) {
          // 스트리밍 완료
          onComplete(data.full_response);
        }
      }
    }
  }
}
```

---

### Generate 엔드포인트

#### `POST /api/v1/generate`

**용도**: 법률 관련 콘텐츠 자동 생성

**요청 본문 구조**:
```json
{
  "topic": "콘텐츠 주제",
  "content_type": "blog" | "article" | "opinion" | "analysis" | "faq",
  "style": "전문적" | "대중적" | "간결한",
  "target_length": 3000,
  "include_sections": ["법적기준", "판례", "대응방법"],
  "keywords": ["사기", "가중처벌"],
  "document_types": ["statute", "case"],
  "n_references": 10
}
```

**응답 구조**:
```json
{
  "success": true,
  "content": "생성된 콘텐츠 전체",
  "title": "콘텐츠 제목",
  "sections": {
    "섹션 제목": "섹션 내용"
  },
  "references": [
    {
      "title": "참고 문서 제목",
      "type": "statute",
      "id": "문서-ID",
      "relevance": 0.95
    }
  ],
  "metadata": {
    "content_type": "blog",
    "topic": "주제",
    "word_count": 2847
  },
  "timestamp": "2025-12-09T14:30:00.123456"
}
```

**콘텐츠 타입별 구조**:

1. **blog**:
   - 제목 (SEO 최적화)
   - 도입부
   - 법적 기준과 처벌
   - 실제 사례와 판례
   - 대응 방법과 예방책
   - 전문가 조언
   - 마무리

2. **article**:
   - 제목
   - 기사 본문
   - 관련 법령 및 판례 인용
   - 시사점 및 전망

3. **opinion**:
   - 의견서 제목
   - 사실관계
   - 법적 쟁점
   - 관련 법령 및 판례
   - 법리적 분석
   - 결론 및 의견

4. **analysis**:
   - 분석 제목
   - 사건 개요
   - 법적 쟁점
   - 관련 법령 검토
   - 관련 판례 분석
   - 법리적 판단
   - 시사점

5. **faq**:
   - 질문과 답변 형식
   - 법적 정의 및 기준
   - 처벌 및 법적 효과
   - 실제 사례
   - 대응 방법
   - 전문가 상담 필요성

---

### Admin 엔드포인트 (🔒 API 키 필요)

#### `POST /api/v1/admin/upload`

**용도**: JSON 파일을 업로드하여 즉시 인덱싱

**인증**: API 키 필요 (X-API-Key 헤더)

**파라미터**:
- `file` (multipart/form-data): 업로드할 JSON 파일

**파일 형식 요구사항**:
- JSON 형식이어야 합니다
- 다음 중 하나의 문서 타입 스키마를 따라야 합니다:
  - `StatuteDocument`: 법령 문서
  - `CaseDocument`: 판례 문서
  - `ProcedureDocument`: 절차 문서
  - `TemplateDocument`: 템플릿 문서
  - `ManualDocument`: 매뉴얼 문서
  - `FAQDocument`: FAQ 문서

**응답**:
```json
{
  "success": true,
  "message": "문서가 성공적으로 인덱싱되었습니다.",
  "document_id": "statute-형법-347",
  "chunks_count": 3
}
```

**에러 응답**:
- `400`: 유효하지 않은 JSON 파일
- `401`: API 키 없음 또는 잘못됨
- `500`: 인덱싱 실패

---

#### `POST /api/v1/admin/index`

**용도**: 디렉토리의 모든 JSON 파일을 일괄 인덱싱

**인증**: API 키 필요

**요청 본문**:
```json
{
  "directory": "data/processed/statutes",
  "pattern": "*.json",
  "chunk": true
}
```

**파라미터**:
- `directory` (필수): 인덱싱할 디렉토리 경로
- `pattern` (선택): 파일 패턴 (기본값: `"*.json"`)
- `chunk` (선택): 청킹 여부 (기본값: `true`)

**응답**:
```json
{
  "success": true,
  "total": 100,
  "indexed": 95,
  "failed": 5,
  "details": [
    {
      "file": "statute-347.json",
      "success": true,
      "chunks_count": 3
    },
    {
      "file": "invalid.json",
      "success": false,
      "error": "유효하지 않은 JSON 형식"
    }
  ]
}
```

---

#### `POST /api/v1/admin/index/incremental`

**용도**: 새로 추가되거나 변경된 문서만 인덱싱 (증분 업데이트)

**인증**: API 키 필요

**Query Parameters**:
- `directory` (필수): 디렉토리 경로
- `pattern` (선택): 파일 패턴 (기본값: `"*.json"`)

**응답**:
```json
{
  "success": true,
  "total": 10,
  "new": 5,
  "updated": 2,
  "skipped": 3,
  "failed": 0
}
```

**작동 원리**:
- `data/index_state.json` 파일에 인덱싱된 파일 목록이 저장됩니다
- 이전에 인덱싱된 파일은 건너뜁니다
- 새 파일이나 수정된 파일만 인덱싱합니다

---

#### `GET /api/v1/admin/index/status`

**용도**: 인덱스 상태 조회 (API 키 불필요)

**응답**:
```json
{
  "collection_name": "legal_documents",
  "document_count": 821,
  "indexed_documents": 150,
  "health_status": {
    "status": "healthy",
    "vector_db_count": 821,
    "indexed_documents": 150,
    "timestamp": "2025-12-09T14:20:55.404392"
  }
}
```

**필드 설명**:
- `document_count`: 벡터 DB에 저장된 총 청크 수
- `indexed_documents`: 인덱싱된 원본 문서 수
- `health_status.status`: 
  - `"healthy"`: 정상
  - `"empty"`: 데이터 없음
  - `"error"`: 오류 발생

---

#### `POST /api/v1/admin/index/reset`

**용도**: 벡터 DB 초기화 (모든 데이터 삭제)

**인증**: API 키 필요

**주의**: 이 작업은 되돌릴 수 없습니다! 모든 인덱싱된 데이터가 삭제됩니다.

**응답**:
```json
{
  "success": true,
  "message": "인덱스가 초기화되었습니다."
}
```

---

### Monitoring 엔드포인트

#### `GET /api/v1/monitoring/stats`

**용도**: API 통계 및 성능 메트릭 조회

**인증**: 불필요

**응답**:
```json
{
  "api": {
    "total_requests": 1250,
    "successful_requests": 1200,
    "failed_requests": 50,
    "average_response_time": 0.45
  },
  "search": {
    "total_searches": 800,
    "average_search_time": 0.32,
    "cache_hit_rate": 0.65
  },
  "llm": {
    "total_queries": 450,
    "average_generation_time": 2.15,
    "total_tokens_used": 125000
  }
}
```

---

#### `GET /api/v1/monitoring/vector-db`

**용도**: 벡터 DB 상세 상태 조회

**인증**: API 키 필요

**응답**:
```json
{
  "current_status": {
    "connected": true,
    "collection_exists": true,
    "document_count": 821
  },
  "summary": {
    "status": "healthy",
    "message": "벡터 DB가 정상적으로 작동 중입니다."
  }
}
```

---

## ⚠️ 주의사항 및 모범 사례

### 1. API 키 인증

#### API 키가 필요한 엔드포인트
- `/api/v1/admin/*`: 모든 관리자 엔드포인트
- `/api/v1/monitoring/vector-db`: 벡터 DB 상세 상태

#### API 키 설정 방법

**환경 변수로 설정** (권장):
```powershell
# .env 파일에 추가
API_KEY=your-secret-api-key-here
```

**Swagger UI에서 사용**:
1. 상단의 "Authorize" 버튼 클릭
2. 팝업 창에 API 키 입력
3. "Authorize" 클릭
4. 🔒 아이콘이 채워진 상태로 변경되면 인증 완료

**cURL에서 사용**:
```bash
curl -X POST "http://localhost:8000/api/v1/admin/upload" \
  -H "X-API-Key: your-secret-api-key-here" \
  -F "file=@document.json"
```

**보안 주의사항**:
- API 키는 절대 공개하지 마세요
- 프로덕션 환경에서는 강력한 API 키를 사용하세요
- API 키는 정기적으로 변경하는 것을 권장합니다

---

### 2. 필수 필드 및 데이터 검증

#### 필수 필드 표시
- 빨간색 별표(*)가 있는 필드는 필수입니다
- 필수 필드를 입력하지 않으면 `422 Unprocessable Entity` 오류가 발생합니다

#### 데이터 타입 주의사항

**문자열 (string)**:
- 따옴표로 감싸야 합니다: `"사기죄"`
- 숫자도 문자열로 전달해야 하는 경우가 있습니다

**숫자 (integer)**:
- 따옴표 없이 입력: `5` (올바름), `"5"` (잘못됨)
- 범위 제한이 있는 경우 확인: `n_results`는 1~20 사이

**배열 (array)**:
- 대괄호로 감싸고 쉼표로 구분: `["statute", "case"]`
- 빈 배열도 가능: `[]`
- null도 가능: `null` 또는 필드 생략

**불린 (boolean)**:
- `true` 또는 `false` (소문자)
- 따옴표 없이 입력: `true` (올바름), `"true"` (잘못됨)

#### 데이터 검증 오류 예시

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "n_results"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge",
      "ctx": {"limit_value": 1}
    }
  ]
}
```
- `n_results`가 1보다 작은 경우

```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
- 필수 필드 `query`가 누락된 경우

---

### 3. 에러 처리 및 문제 해결

#### HTTP 상태 코드

| 코드 | 의미 | 원인 | 해결 방법 |
|------|------|------|----------|
| `200` | 성공 | - | - |
| `400` | 잘못된 요청 | 요청 본문 형식 오류 | JSON 형식 확인 |
| `401` | 인증 실패 | API 키 없음 또는 잘못됨 | API 키 확인 |
| `422` | 검증 실패 | 필수 필드 누락 또는 값 오류 | 필드 값 확인 |
| `429` | 요청 한도 초과 | Rate limit 초과 | 잠시 후 재시도 |
| `500` | 서버 오류 | 내부 서버 문제 | 서버 로그 확인 |

#### 일반적인 오류 및 해결

**1. "검색 결과가 없습니다" (results: [])**

**원인**:
- 데이터가 인덱싱되지 않음
- 검색 쿼리가 너무 구체적이거나 필터가 너무 엄격함

**해결**:
```powershell
# 인덱싱 상태 확인
python scripts/check_indexed_data.py

# 데이터 인덱싱
python scripts/process_and_index.py --input-dir data/processed/statutes --doc-type statute
```

**2. "API 키가 필요합니다" (401)**

**원인**: 관리자 엔드포인트에 API 키 없이 접근

**해결**:
1. `.env` 파일에 `API_KEY` 설정
2. Swagger UI에서 "Authorize" 버튼 클릭하여 API 키 입력

**3. "Rate limit exceeded" (429)**

**원인**: 분당 요청 수 제한 초과

**해결**:
- 잠시 기다린 후 재시도
- `n_results` 값을 줄여서 요청 수 감소
- Rate limit 설정 확인: `config/settings.py`

**4. "벡터 검색 실패" (500)**

**원인**: 벡터 DB 연결 실패 또는 임베딩 생성 실패

**해결**:
1. 벡터 DB 상태 확인: `GET /api/v1/health/detailed`
2. OpenAI API 키 확인
3. 네트워크 연결 확인

---

### 4. 성능 최적화 팁

#### 검색 성능 향상

1. **필터 활용**:
   - `document_types`로 검색 범위 축소
   - `category`, `sub_category`로 더 정확한 결과
   - 불필요한 필터는 제거

2. **결과 수 조절**:
   - `n_results`를 필요한 만큼만 설정 (5~10개 권장)
   - 많은 결과가 필요하면 여러 번 검색

3. **캐싱 활용**:
   - 동일한 쿼리는 캐시에서 빠르게 반환됩니다
   - 캐시는 자동으로 활성화되어 있습니다

#### 질의응답 성능 향상

1. **세션 관리**:
   - `session_id`를 사용하여 연속 대화 유지
   - 불필요한 세션은 삭제 (세션은 자동으로 만료됨)

2. **문서 타입 필터**:
   - 필요한 문서 타입만 지정하여 검색 시간 단축

3. **스트리밍 사용**:
   - 긴 답변이 예상되면 `/api/v1/ask/stream` 사용
   - 사용자 경험 향상

---

### 5. 보안 모범 사례

#### API 키 관리

1. **환경 변수 사용**:
   - `.env` 파일에 저장 (Git에 커밋하지 않음)
   - `.gitignore`에 `.env` 추가 확인

2. **강력한 키 사용**:
   - 최소 32자 이상
   - 랜덤 문자열 사용
   - 정기적으로 변경

3. **접근 제한**:
   - 관리자 엔드포인트는 신뢰할 수 있는 사용자만 접근
   - 프로덕션에서는 IP 화이트리스트 고려

#### 요청 데이터 검증

1. **입력 검증**:
   - 모든 사용자 입력은 검증됩니다
   - 악의적인 입력은 자동으로 차단됩니다

2. **Rate Limiting**:
   - DDoS 공격 방지
   - 경로별로 다른 제한 적용

---

### 6. 데이터 형식 가이드

#### 검색 쿼리 작성 팁

**효과적인 쿼리**:
- ✅ `"형법 제347조"` - 구체적인 법령 조문
- ✅ `"사기죄 처벌"` - 명확한 키워드
- ✅ `"사기 판례에서 중요한 기준"` - 자연어 질문

**비효과적인 쿼리**:
- ❌ `"법"` - 너무 일반적
- ❌ `"ㅅㄱ"` - 오타 또는 축약어
- ❌ `"법률에 대해 알려주세요"` - 너무 모호함

#### 필터 조합 전략

**예시 1: 특정 법령만 검색**
```json
{
  "query": "사기",
  "document_types": ["statute"],
  "category": "형사"
}
```

**예시 2: 최근 판례만 검색**
```json
{
  "query": "사기",
  "document_types": ["case"],
  "category": "형사",
  "sub_category": "사기"
}
```

**예시 3: 모든 타입에서 검색**
```json
{
  "query": "사기",
  "n_results": 10
}
```
- 필터를 지정하지 않으면 모든 타입에서 검색됩니다

---

## 🎓 실전 예제 및 시나리오

### 시나리오 1: 형사 사기 관련 법령 검색

**목적**: 형사 사기 관련 법령만 검색하여 정확한 법적 기준 확인

**단계**:
1. `POST /api/v1/search` 선택
2. "Try it out" 클릭
3. 다음 JSON 입력:
   ```json
   {
     "query": "형사 사기죄",
     "n_results": 10,
     "document_types": ["statute"],
     "category": "형사",
     "sub_category": "사기"
   }
   ```
4. "Execute" 클릭
5. 결과 확인

**예상 결과**:
- 형법 제347조(사기) 관련 조문
- 특정경제범죄 가중처벌 등에 관한 법률 관련 조문
- 각 조문의 상세 내용과 메타데이터

**활용**: 법령 조문을 정확히 인용하여 법률 문서 작성 시 참고

---

### 시나리오 2: 판례 기반 질의응답

**목적**: 판례에서 중요한 판단 기준을 AI가 분석하여 답변

**단계**:
1. `POST /api/v1/ask` 선택
2. "Try it out" 클릭
3. 다음 JSON 입력:
   ```json
   {
     "query": "사기죄 판례에서 중요한 판단 기준은 무엇인가요?",
     "document_types": ["case"],
     "stream": false
   }
   ```
4. "Execute" 클릭
5. AI 답변과 참조 판례 확인

**예상 답변**:
- 사기죄의 성립 요건 (기망, 착오, 처분행위, 재산상 이익 취득)
- 판례에서 강조하는 판단 기준
- 실제 판례 인용 (대법원 판례 등)
- 참조 문서 목록

**활용**: 법률 상담 시 판례 기준을 빠르게 파악

---

### 시나리오 3: 연속 대화를 통한 심화 질문

**목적**: 대화 맥락을 유지하며 점진적으로 질문 심화

**1단계: 기본 질문**
```json
{
  "query": "사기죄는 무엇인가요?",
  "session_id": "consultation-001"
}
```

**응답 예시**:
```json
{
  "query": "사기죄는 무엇인가요?",
  "response": "사기죄는 형법 제347조에 규정된 범죄로, 타인을 기망하여 착오에 빠뜨리고 재물을 교부받거나 재산상 이익을 얻는 범죄입니다...",
  "session_id": "consultation-001",
  "sources": [...]
}
```

**2단계: 처벌에 대한 질문** (같은 세션)
```json
{
  "query": "그럼 처벌은 어떻게 되나요?",
  "session_id": "consultation-001"
}
```

**응답 특징**:
- "그럼"이 "사기죄"를 가리킨다는 것을 이해
- 이전 대화에서 언급한 내용을 기반으로 답변
- 사기죄의 처벌에 대해 상세히 설명

**3단계: 판례 질문** (계속)
```json
{
  "query": "판례에서 중요한 기준은?",
  "session_id": "consultation-001"
}
```

**응답 특징**:
- "사기죄"의 "판례"를 의미한다는 것을 이해
- 사기죄 판례의 중요 기준을 설명

**활용**: 법률 상담 시 자연스러운 대화 흐름 유지

---

### 시나리오 4: 블로그 포스팅 자동 생성

**목적**: 법률 블로그 포스팅을 자동으로 생성

**단계**:
1. `POST /api/v1/generate` 선택
2. "Try it out" 클릭
3. 다음 JSON 입력:
   ```json
   {
     "topic": "사기죄 처벌과 대응방법",
     "content_type": "blog",
     "style": "대중적",
     "target_length": 2000,
     "include_sections": ["법적기준", "실제사례", "대응방법"],
     "keywords": ["사기", "처벌", "대응"],
     "document_types": ["statute", "case"],
     "n_references": 8
   }
   ```
4. "Execute" 클릭
5. 생성된 블로그 포스팅 확인

**예상 결과**:
- SEO 최적화된 제목
- 독자 친화적인 문체
- 법적 기준 설명
- 실제 판례 인용
- 실용적인 대응 방법
- 전문가 조언

**활용**: 법률 블로그 운영 시 콘텐츠 자동 생성

---

### 시나리오 5: 법률 의견서 작성

**목적**: 특정 사건에 대한 법률 의견서 자동 생성

**단계**:
1. `POST /api/v1/generate` 선택
2. "Try it out" 클릭
3. 다음 JSON 입력:
   ```json
   {
     "topic": "특정경제범죄 가중처벌법 위반 사건에 대한 법률 의견",
     "content_type": "opinion",
     "style": "전문적",
     "target_length": 5000,
     "include_sections": ["사실관계", "법적쟁점", "법리적분석", "결론"],
     "keywords": ["특경법", "가중처벌", "사기"],
     "document_types": ["statute", "case"],
     "n_references": 15
   }
   ```
4. "Execute" 클릭
5. 생성된 의견서 확인

**활용**: 법률 사무소에서 의견서 초안 작성 시 활용

---

### 시나리오 6: FAQ 자동 생성

**목적**: 자주 묻는 질문과 답변을 자동으로 생성

**단계**:
1. `POST /api/v1/generate` 선택
2. "Try it out" 클릭
3. 다음 JSON 입력:
   ```json
   {
     "topic": "사기죄 관련 자주 묻는 질문",
     "content_type": "faq",
     "style": "간결한",
     "include_sections": ["정의", "처벌", "사례", "대응"],
     "document_types": ["statute", "case"],
     "n_references": 5
   }
   ```
4. "Execute" 클릭
5. 생성된 FAQ 확인

**활용**: 웹사이트 FAQ 섹션 자동 생성

---

### 시나리오 7: 인덱싱 상태 모니터링

**목적**: 데이터 인덱싱 상태를 주기적으로 확인

**단계**:
1. `GET /api/v1/admin/index/status` 선택
2. "Try it out" 클릭
3. "Execute" 클릭
4. 상태 확인

**확인 사항**:
- `document_count > 0`: 데이터가 인덱싱되어 있음
- `health_status.status == "healthy"`: 시스템 정상
- `indexed_documents`: 인덱싱된 원본 문서 수

**활용**: 
- 배치 작업 후 인덱싱 확인
- 시스템 모니터링
- 문제 진단

---

### 시나리오 8: 증분 인덱싱으로 새 문서 추가

**목적**: 새로 추가된 문서만 효율적으로 인덱싱

**전제 조건**: API 키 인증 필요

**단계**:
1. "Authorize" 버튼으로 API 키 입력
2. `POST /api/v1/admin/index/incremental` 선택
3. "Try it out" 클릭
4. Query Parameters 입력:
   - `directory`: `"data/processed/statutes"`
   - `pattern`: `"*.json"` (기본값)
5. "Execute" 클릭
6. 결과 확인

**예상 결과**:
```json
{
  "success": true,
  "total": 10,
  "new": 5,
  "updated": 2,
  "skipped": 3,
  "failed": 0
}
```

**활용**: 
- 새로운 법령이 추가되었을 때
- 판례가 업데이트되었을 때
- 효율적인 데이터 관리

---

## 🔧 문제 해결 가이드

### "Try it out" 버튼이 작동하지 않을 때

**증상**: 버튼을 클릭해도 파라미터 입력 폼이 활성화되지 않음

**해결 방법**:
1. 페이지를 새로고침 (F5 또는 Ctrl+R)
2. 브라우저 캐시 삭제
3. 다른 브라우저에서 시도
4. 서버가 실행 중인지 확인: `http://localhost:8000/health` 접속

---

### 요청이 실패할 때

#### 증상 1: 422 Validation Error

**원인**: 요청 본문 형식 오류 또는 필수 필드 누락

**해결**:
1. JSON 형식 확인 (따옴표, 쉼표, 대괄호 등)
2. 필수 필드 확인 (빨간색 별표 표시)
3. 데이터 타입 확인 (문자열은 따옴표, 숫자는 따옴표 없음)

**예시**:
```json
// ❌ 잘못된 예시
{
  "query": 사기죄,  // 따옴표 없음
  "n_results": "5"  // 숫자에 따옴표
}

// ✅ 올바른 예시
{
  "query": "사기죄",
  "n_results": 5
}
```

#### 증상 2: 500 Internal Server Error

**원인**: 서버 내부 오류

**해결**:
1. 서버 로그 확인: `logs/app.log` 파일 확인
2. 벡터 DB 상태 확인: `GET /api/v1/health/detailed`
3. OpenAI API 키 확인: 환경 변수 `OPENAI_API_KEY` 확인
4. 데이터 인덱싱 확인: `python scripts/check_indexed_data.py`

#### 증상 3: 401 Unauthorized

**원인**: API 키 없음 또는 잘못됨

**해결**:
1. `.env` 파일에 `API_KEY` 설정 확인
2. Swagger UI에서 "Authorize" 버튼으로 API 키 입력
3. API 키가 올바른지 확인

#### 증상 4: 429 Too Many Requests

**원인**: Rate limit 초과

**해결**:
1. 잠시 기다린 후 재시도 (1분 후)
2. `n_results` 값을 줄여서 요청 수 감소
3. Rate limit 설정 확인: `config/settings.py`의 `RATE_LIMIT_*` 설정

---

### 응답이 느릴 때

**원인 및 해결**:

1. **검색 결과가 많을 때**:
   - `n_results` 값을 줄이기 (5~10개 권장)
   - 필터 사용하여 검색 범위 축소

2. **임베딩 생성이 느릴 때**:
   - OpenAI API 응답 시간에 의존
   - 네트워크 연결 확인
   - 캐시 활용 (동일한 쿼리는 캐시에서 빠르게 반환)

3. **LLM 응답 생성이 느릴 때**:
   - 긴 답변이 필요한 경우 스트리밍 사용 (`/api/v1/ask/stream`)
   - `document_types` 필터로 검색 시간 단축

---

### 검색 결과가 없을 때 (results: [])

**원인**:
- 데이터가 인덱싱되지 않음
- 검색 쿼리가 너무 구체적이거나 필터가 너무 엄격함
- 벡터 DB에 데이터가 없음

**해결**:
1. 인덱싱 상태 확인:
   ```powershell
   python scripts/check_indexed_data.py
   ```

2. 데이터 인덱싱:
   ```powershell
   python scripts/process_and_index.py --input-dir data/processed/statutes --doc-type statute
   python scripts/process_and_index.py --input-dir data/processed/cases --doc-type case
   ```

3. 필터 완화:
   - `document_types` 필터 제거
   - `category`, `sub_category` 필터 제거
   - 더 일반적인 검색어 사용

4. 벡터 DB 확인:
   ```powershell
   # 벡터 DB 상태 확인
   GET /api/v1/admin/index/status
   ```

---

### 스트리밍 응답이 작동하지 않을 때

**증상**: `/api/v1/ask/stream` 엔드포인트에서 응답이 오지 않음

**원인**:
- Swagger UI는 스트리밍 응답을 완전히 지원하지 않을 수 있음
- 브라우저 호환성 문제

**해결**:
1. cURL로 테스트:
   ```bash
   curl -N -X POST "http://localhost:8000/api/v1/ask/stream" \
     -H "Content-Type: application/json" \
     -d '{"query": "사기죄는?"}'
   ```

2. JavaScript EventSource 사용:
   ```javascript
   const eventSource = new EventSource('/api/v1/ask/stream', {
     method: 'POST',
     body: JSON.stringify({query: "사기죄는?"})
   });
   ```

3. 일반 질의응답 사용: `/api/v1/ask` 엔드포인트 사용

---

## 📚 추가 리소스 및 참고 자료

### API 문서

- **Swagger UI**: http://localhost:8000/docs (현재 문서)
- **ReDoc**: http://localhost:8000/redoc (다른 스타일의 API 문서, 더 읽기 쉬움)
- **OpenAPI 스키마**: http://localhost:8000/openapi.json (JSON 형식, 자동화 도구에서 사용)

### 관련 가이드 문서

- **사용 가이드**: `docs/guides/USAGE_GUIDE.md` - 전체 시스템 사용법
- **데이터 전처리 가이드**: `docs/guides/DATA_PREPROCESSING_EASY_GUIDE.md` - 데이터 준비 방법
- **RAG 데이터 빌드 가이드**: `docs/guides/RAG_DATA_BUILD_GUIDE.md` - RAG 시스템 구축 방법
- **인덱싱 확인 가이드**: `docs/guides/CHECK_INDEXED_DATA.md` - 인덱싱 상태 확인 방법

### 개발자 리소스

- **프로젝트 README**: `README.md` - 프로젝트 개요 및 설치 방법
- **코드 분석**: `docs/project/CODE_ANALYSIS.md` - 코드 구조 분석
- **제작 순서**: `docs/project/제작_순서_계획서.md` - 개발 계획

### 외부 도구

- **Postman**: Swagger UI 대신 사용 가능한 API 테스트 도구
- **Insomnia**: 또 다른 API 테스트 도구
- **cURL**: 명령줄에서 API 테스트

---

## 🎯 빠른 참조 (Cheat Sheet)

### 자주 사용하는 엔드포인트

| 엔드포인트 | 메서드 | 용도 | 인증 |
|-----------|--------|------|------|
| `/api/v1/health` | GET | 서버 상태 확인 | ❌ |
| `/api/v1/search` | POST | 문서 검색 | ❌ |
| `/api/v1/ask` | POST | 질의응답 | ❌ |
| `/api/v1/ask/stream` | POST | 스트리밍 질의응답 | ❌ |
| `/api/v1/generate` | POST | 콘텐츠 생성 | ❌ |
| `/api/v1/admin/upload` | POST | 파일 업로드 | ✅ |
| `/api/v1/admin/index/status` | GET | 인덱스 상태 | ❌ |

### 자주 사용하는 필터

```json
// 법령만 검색
{"document_types": ["statute"]}

// 판례만 검색
{"document_types": ["case"]}

// 형사 사기 관련만 검색
{"category": "형사", "sub_category": "사기"}

// 모든 타입 검색 (필터 없음)
{}
```

### 자주 사용하는 cURL 명령어

```bash
# 헬스체크
curl http://localhost:8000/api/v1/health

# 검색 (POST)
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "사기", "n_results": 5}'

# 질의응답
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "사기죄는?"}'

# 인덱스 상태 확인
curl http://localhost:8000/api/v1/admin/index/status
```

---

## ✅ 체크리스트

### 첫 사용 전 확인사항

- [ ] 서버가 실행 중인가요? (`python -m src.api.main`)
- [ ] `.env` 파일에 `OPENAI_API_KEY`가 설정되어 있나요?
- [ ] 데이터가 인덱싱되어 있나요? (`python scripts/check_indexed_data.py`)
- [ ] Swagger UI에 접속할 수 있나요? (`http://localhost:8000/docs`)

### API 사용 전 확인사항

- [ ] 요청 본문이 올바른 JSON 형식인가요?
- [ ] 필수 필드를 모두 입력했나요?
- [ ] 데이터 타입이 올바른가요? (문자열은 따옴표, 숫자는 따옴표 없음)
- [ ] 관리자 엔드포인트 사용 시 API 키를 입력했나요?

### 문제 발생 시 확인사항

- [ ] 서버 로그를 확인했나요? (`logs/app.log`)
- [ ] 헬스체크 엔드포인트가 정상인가요? (`GET /api/v1/health`)
- [ ] 벡터 DB 상태가 정상인가요? (`GET /api/v1/health/detailed`)
- [ ] 네트워크 연결이 정상인가요?

---

이제 Swagger UI를 사용하여 IBS 법률 AI 시스템 API를 완전히 활용할 수 있습니다! 🎉

**추가 도움이 필요하시면**:
- 프로젝트 README 참조
- 관련 가이드 문서 참조
- 서버 로그 확인
- GitHub Issues에 문의

