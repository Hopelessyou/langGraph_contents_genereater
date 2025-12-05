# IBS 법률 AI 시스템 API 문서

## 개요

IBS 법률 AI 시스템은 법률 정보 RAG(Retrieval-Augmented Generation) 기반 질의응답 API를 제공합니다.

**Base URL**: `http://localhost:8000/api/v1`

## 인증

관리자 API는 API 키 인증이 필요합니다.

**헤더**:
```
X-API-Key: your_api_key_here
```

환경 변수 `API_KEY`에 설정된 값과 일치해야 합니다.

## 엔드포인트

### 헬스체크

#### GET /health
기본 헬스체크

**응답**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### GET /health/detailed
상세 헬스체크 (컴포넌트별 상태 포함)

### 검색 API

#### POST /search
문서 검색

**요청 본문**:
```json
{
  "query": "사기 범죄",
  "n_results": 5,
  "document_types": ["statute", "case"],
  "category": "형사",
  "sub_category": "사기"
}
```

**응답**:
```json
{
  "query": "사기 범죄",
  "results": [
    {
      "id": "statute-347",
      "document": "법령 내용...",
      "metadata": {...},
      "distance": 0.123,
      "score": 0.89
    }
  ],
  "total": 5,
  "timestamp": "2024-01-01T00:00:00"
}
```

#### GET /search
GET 방식 검색 (쿼리 파라미터 사용)

### 질의응답 API

#### POST /ask
질의응답

**요청 본문**:
```json
{
  "query": "사기 초범은 집행유예가 가능한가요?",
  "session_id": "optional-session-id",
  "stream": false,
  "document_types": ["statute", "case"]
}
```

**응답**:
```json
{
  "query": "사기 초범은 집행유예가 가능한가요?",
  "response": "답변 내용...",
  "session_id": "session-uuid",
  "sources": [
    {
      "id": "statute-347",
      "title": "형법 제347조",
      "type": "statute"
    }
  ],
  "timestamp": "2024-01-01T00:00:00"
}
```

#### POST /ask/stream
스트리밍 질의응답 (Server-Sent Events)

### 관리자 API

#### POST /admin/index
문서 인덱싱

**요청 본문**:
```json
{
  "directory": "./data/samples",
  "pattern": "*.json",
  "chunk": true
}
```

#### POST /admin/index/incremental
증분 인덱싱

#### GET /admin/index/status
인덱스 상태 조회

#### POST /admin/index/reset
인덱스 초기화

#### POST /admin/upload
문서 업로드 및 인덱싱

### 모니터링 API

#### GET /monitoring/stats
모니터링 통계 조회

#### GET /monitoring/vector-db
벡터 DB 상태 조회 (인증 필요)

## 에러 응답

모든 API는 표준 HTTP 상태 코드를 사용합니다:

- `200`: 성공
- `400`: 잘못된 요청
- `401`: 인증 실패
- `404`: 리소스를 찾을 수 없음
- `429`: 요청 한도 초과
- `500`: 내부 서버 오류

**에러 응답 형식**:
```json
{
  "error": "에러 메시지",
  "detail": "상세 정보"
}
```

