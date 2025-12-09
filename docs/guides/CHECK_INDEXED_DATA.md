# 데이터 인덱싱 확인 방법 📊

벡터 DB에 데이터가 제대로 인덱싱되었는지 확인하는 여러 방법을 안내합니다.

---

## 목차

1. [가장 쉬운 방법: API 사용](#1-가장-쉬운-방법-api-사용)
2. [Python 코드로 확인](#2-python-코드로-확인)
3. [검색 테스트로 확인](#3-검색-테스트로-확인)
4. [벡터 DB 직접 확인](#4-벡터-db-직접-확인)

---

## 1. 가장 쉬운 방법: API 사용

### 1.1 인덱스 상태 확인 (Swagger UI)

**단계:**
1. 서버 실행: `python -m src.api.main`
2. 브라우저에서 http://localhost:8000/docs 접속
3. `GET /api/v1/admin/index/status` 엔드포인트 클릭
4. "Try it out" → "Execute" 클릭

**응답 예시:**
```json
{
  "collection_name": "legal_documents",
  "document_count": 150,
  "indexed_documents": 150,
  "health_status": {
    "status": "healthy",
    "vector_db_count": 450,
    "indexed_documents": 150,
    "timestamp": "2024-12-09T12:00:00"
  }
}
```

**의미:**
- `document_count`: 벡터 DB에 저장된 청크 수
- `indexed_documents`: 인덱싱된 문서 수
- `health_status.status`: "healthy"면 정상

### 1.2 cURL로 확인

```bash
# 인덱스 상태 확인
curl http://localhost:8000/api/v1/admin/index/status

# 벡터 DB 상태 확인 (인증 필요)
curl -X GET "http://localhost:8000/api/v1/monitoring/vector-db" \
  -H "X-API-Key: your_api_key"
```

### 1.3 Python requests로 확인

```python
import requests

# 인덱스 상태 확인
response = requests.get("http://localhost:8000/api/v1/admin/index/status")
status = response.json()

print(f"컬렉션 이름: {status['collection_name']}")
print(f"벡터 DB 문서 수: {status['document_count']}")
print(f"인덱싱된 문서 수: {status['indexed_documents']}")
print(f"상태: {status['health_status']['status']}")
```

---

## 2. Python 코드로 확인

### 2.1 벡터 DB 문서 수 확인

```python
from src.rag.vector_store import VectorStore

# 벡터 스토어 생성
vector_store = VectorStore(collection_name="legal_documents")

# 문서 수 확인
count = vector_store.get_count()
print(f"벡터 DB에 저장된 청크 수: {count}개")

# 컬렉션 정보 확인
print(f"컬렉션 이름: {vector_store.collection_name}")
```

### 2.2 인덱싱 상태 상세 확인

```python
from src.rag import DocumentIndexer
from src.rag.incremental_updater import IncrementalUpdater
from src.rag.monitor import IndexMonitor

# 인덱서 생성
indexer = DocumentIndexer()
updater = IncrementalUpdater(indexer)
monitor = IndexMonitor(indexer.vector_store, updater)

# 상태 확인
status = updater.get_status()
health = monitor.get_health_status()
statistics = monitor.get_statistics()

print("=" * 60)
print("📊 인덱싱 상태")
print("=" * 60)
print(f"인덱싱된 문서 수: {status['indexed_count']}")
print(f"벡터 DB 청크 수: {health['vector_db_count']}")
print(f"상태: {health['status']}")
print(f"문서당 평균 청크 수: {statistics.get('average_chunks_per_document', 0):.1f}")

# 일관성 확인
consistency = monitor.check_consistency()
if consistency['consistent']:
    print("✅ 인덱스 일관성: 정상")
else:
    print("❌ 인덱스 일관성: 문제 발견")
    for issue in consistency['issues']:
        print(f"   - {issue}")
```

### 2.3 특정 문서 검색으로 확인

```python
from src.rag.vector_store import VectorStore
from src.rag.embedding import EmbeddingGenerator

# 벡터 스토어와 임베딩 생성기 생성
vector_store = VectorStore()
embedding_gen = EmbeddingGenerator()

# 테스트 쿼리
test_query = "사기 범죄"

# 임베딩 생성
query_embedding = await embedding_gen.embed_text(test_query)

# 검색
results = await vector_store.search(
    query_embedding=query_embedding,
    n_results=5
)

print(f"검색 결과: {len(results.get('ids', [])[0]) if results.get('ids') else 0}개")
if results.get('ids'):
    print("\n검색된 문서:")
    for i, doc_id in enumerate(results['ids'][0], 1):
        print(f"{i}. {doc_id}")
        if results.get('metadatas') and results['metadatas'][0]:
            metadata = results['metadatas'][0][i-1]
            print(f"   제목: {metadata.get('title', 'N/A')}")
            print(f"   타입: {metadata.get('type', 'N/A')}")
```

---

## 3. 검색 테스트로 확인

### 3.1 Swagger UI에서 검색 테스트

**단계:**
1. http://localhost:8000/docs 접속
2. `POST /api/v1/search` 엔드포인트 클릭
3. "Try it out" 클릭
4. 요청 본문 입력:
   ```json
   {
     "query": "사기 범죄",
     "n_results": 5
   }
   ```
5. "Execute" 클릭

**결과 확인:**
- 결과가 나오면 → 데이터가 정상적으로 인덱싱됨 ✅
- 결과가 없으면 → 데이터가 없거나 인덱싱 안 됨 ❌

### 3.2 Python으로 검색 테스트

```python
import requests

# 검색 테스트
response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "사기 범죄",
        "n_results": 5
    }
)

results = response.json()

if results.get('results'):
    print(f"✅ 검색 성공: {len(results['results'])}개 결과")
    for i, result in enumerate(results['results'], 1):
        print(f"{i}. {result.get('metadata', {}).get('title', 'N/A')}")
else:
    print("❌ 검색 결과 없음 - 데이터가 인덱싱되지 않았을 수 있습니다.")
```

### 3.3 질의응답 테스트

```python
import requests

# 질의응답 테스트
response = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={
        "query": "사기 범죄에 대해 알려주세요",
        "stream": False
    }
)

answer = response.json()

if answer.get('response'):
    print("✅ 질의응답 성공!")
    print(f"답변: {answer['response'][:200]}...")
    print(f"출처: {len(answer.get('sources', []))}개")
else:
    print("❌ 질의응답 실패 - 데이터가 없을 수 있습니다.")
```

---

## 4. 벡터 DB 직접 확인

### 4.1 ChromaDB 직접 접근

```python
import chromadb
from chromadb.config import Settings

# ChromaDB 클라이언트 생성
client = chromadb.PersistentClient(
    path="./data/vector_db",
    settings=Settings(anonymized_telemetry=False)
)

# 컬렉션 가져오기
collection = client.get_collection("legal_documents")

# 문서 수 확인
count = collection.count()
print(f"벡터 DB 문서 수: {count}개")

# 샘플 데이터 확인 (최대 10개)
results = collection.get(limit=10)
print(f"\n샘플 문서 ID:")
for i, doc_id in enumerate(results['ids'][:10], 1):
    print(f"{i}. {doc_id}")
    if results.get('metadatas'):
        metadata = results['metadatas'][i-1] if i-1 < len(results['metadatas']) else {}
        print(f"   제목: {metadata.get('title', 'N/A')}")
        print(f"   타입: {metadata.get('type', 'N/A')}")
```

### 4.2 특정 문서 ID로 확인

```python
import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(path="./data/vector_db")
collection = client.get_collection("legal_documents")

# 특정 문서 ID로 검색
document_id = "case-2010도12928"
results = collection.get(
    where={"document_id": document_id},
    limit=10
)

if results['ids']:
    print(f"✅ 문서 '{document_id}' 발견: {len(results['ids'])}개 청크")
    for i, chunk_id in enumerate(results['ids'], 1):
        print(f"{i}. 청크 ID: {chunk_id}")
        if results.get('documents'):
            print(f"   내용: {results['documents'][i-1][:100]}...")
else:
    print(f"❌ 문서 '{document_id}'를 찾을 수 없습니다.")
```

### 4.3 메타데이터로 필터링 확인

```python
import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(path="./data/vector_db")
collection = client.get_collection("legal_documents")

# 특정 타입의 문서만 확인
results = collection.get(
    where={"type": "case"},  # 판례만
    limit=10
)

print(f"판례 문서: {len(results['ids'])}개 청크")
for i, doc_id in enumerate(results['ids'][:5], 1):
    print(f"{i}. {doc_id}")
```

---

## 5. 완전한 확인 스크립트

### 5.1 종합 확인 스크립트

```python
#!/usr/bin/env python3
"""인덱싱 데이터 종합 확인 스크립트"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.rag import DocumentIndexer, VectorStore, EmbeddingGenerator
from src.rag.incremental_updater import IncrementalUpdater
from src.rag.monitor import IndexMonitor
import asyncio

async def check_indexed_data():
    """인덱싱된 데이터 종합 확인"""
    
    print("=" * 60)
    print("📊 인덱싱 데이터 확인")
    print("=" * 60)
    
    # 1. 벡터 스토어 확인
    print("\n1️⃣ 벡터 DB 상태")
    print("-" * 60)
    vector_store = VectorStore()
    count = await vector_store.get_count()
    print(f"   벡터 DB 청크 수: {count}개")
    print(f"   컬렉션 이름: {vector_store.collection_name}")
    
    if count == 0:
        print("\n⚠️  벡터 DB가 비어있습니다!")
        print("   데이터를 인덱싱하세요:")
        print("   python scripts/process_and_index.py --input-dir data/processed/cases --doc-type case")
        return
    
    # 2. 인덱싱 상태 확인
    print("\n2️⃣ 인덱싱 상태")
    print("-" * 60)
    indexer = DocumentIndexer()
    updater = IncrementalUpdater(indexer)
    monitor = IndexMonitor(indexer.vector_store, updater)
    
    status = updater.get_status()
    health = monitor.get_health_status()
    
    print(f"   인덱싱된 문서 수: {status['indexed_count']}개")
    print(f"   벡터 DB 청크 수: {health['vector_db_count']}개")
    print(f"   상태: {health['status']}")
    
    # 3. 통계 확인
    print("\n3️⃣ 통계")
    print("-" * 60)
    statistics = monitor.get_statistics()
    if statistics.get('average_chunks_per_document'):
        print(f"   문서당 평균 청크 수: {statistics['average_chunks_per_document']:.1f}개")
    
    # 4. 일관성 확인
    print("\n4️⃣ 일관성 확인")
    print("-" * 60)
    consistency = monitor.check_consistency()
    if consistency['consistent']:
        print("   ✅ 인덱스 일관성: 정상")
    else:
        print("   ❌ 인덱스 일관성: 문제 발견")
        for issue in consistency['issues']:
            print(f"      - {issue}")
    
    # 5. 검색 테스트
    print("\n5️⃣ 검색 테스트")
    print("-" * 60)
    embedding_gen = EmbeddingGenerator()
    test_query = "사기 범죄"
    
    query_embedding = await embedding_gen.embed_text(test_query)
    results = await vector_store.search(
        query_embedding=query_embedding,
        n_results=3
    )
    
    if results.get('ids') and len(results['ids'][0]) > 0:
        print(f"   ✅ 검색 성공: '{test_query}' → {len(results['ids'][0])}개 결과")
        print("\n   검색 결과:")
        for i, doc_id in enumerate(results['ids'][0][:3], 1):
            print(f"   {i}. {doc_id}")
            if results.get('metadatas') and results['metadatas'][0]:
                metadata = results['metadatas'][0][i-1]
                print(f"      제목: {metadata.get('title', 'N/A')}")
                print(f"      타입: {metadata.get('type', 'N/A')}")
    else:
        print(f"   ❌ 검색 실패: '{test_query}'에 대한 결과 없음")
    
    # 6. 문서 타입별 통계
    print("\n6️⃣ 문서 타입별 통계")
    print("-" * 60)
    try:
        import chromadb
        from chromadb.config import Settings
        
        client = chromadb.PersistentClient(
            path=str(Path("./data/vector_db")),
            settings=Settings(anonymized_telemetry=False)
        )
        collection = client.get_collection(vector_store.collection_name)
        
        # 모든 문서 가져오기 (메타데이터만)
        all_data = collection.get(limit=1000)
        
        if all_data.get('metadatas'):
            type_counts = {}
            for metadata in all_data['metadatas']:
                doc_type = metadata.get('type', 'unknown')
                type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
            
            for doc_type, count in sorted(type_counts.items()):
                print(f"   {doc_type}: {count}개 청크")
    except Exception as e:
        print(f"   ⚠️  통계 수집 실패: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 확인 완료!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(check_indexed_data())
```

**사용 방법:**
```bash
python scripts/check_indexed_data.py
```

---

## 6. 빠른 확인 체크리스트

### ✅ 데이터가 제대로 들어갔는지 확인하는 방법

1. **벡터 DB 문서 수 확인**
   ```python
   from src.rag.vector_store import VectorStore
   vector_store = VectorStore()
   count = await vector_store.get_count()
   print(f"청크 수: {count}개")  # 0이 아니어야 함
   ```

2. **검색 테스트**
   ```bash
   # Swagger UI에서
   POST /api/v1/search
   {
     "query": "사기",
     "n_results": 5
   }
   ```
   - 결과가 나오면 → 정상 ✅
   - 결과가 없으면 → 문제 ❌

3. **인덱스 상태 API 확인**
   ```bash
   GET http://localhost:8000/api/v1/admin/index/status
   ```
   - `document_count > 0` → 정상 ✅
   - `document_count == 0` → 데이터 없음 ❌

4. **질의응답 테스트**
   ```bash
   POST /api/v1/ask
   {
     "query": "사기 범죄에 대해 알려주세요"
   }
   ```
   - 답변이 나오면 → 정상 ✅
   - 에러가 나면 → 문제 ❌

---

## 7. 문제 해결

### Q1: 벡터 DB 문서 수가 0개입니다

**원인:**
- 데이터가 인덱싱되지 않았음
- 인덱싱 중 에러 발생

**해결:**
```bash
# 다시 인덱싱 실행
python scripts/process_and_index.py \
    --input-dir "data/processed/cases" \
    --doc-type "case"
```

### Q2: 검색 결과가 없습니다

**원인:**
- 데이터가 없음
- 임베딩 생성 실패
- 검색 쿼리가 너무 구체적

**해결:**
```python
# 1. 벡터 DB 확인
vector_store = VectorStore()
count = await vector_store.get_count()
print(f"벡터 DB 문서 수: {count}")

# 2. 더 일반적인 검색어로 테스트
# "사기" → "형법" 또는 "법률"
```

### Q3: 인덱싱은 성공했는데 검색이 안 됩니다

**원인:**
- 임베딩 모델 불일치
- 벡터 DB 경로 문제

**해결:**
```python
# 벡터 DB 경로 확인
from config.settings import settings
print(f"벡터 DB 경로: {settings.chroma_persist_path}")

# 임베딩 모델 확인
print(f"임베딩 모델: {settings.embedding_model}")
```

---

## 8. 자주 사용하는 확인 명령어

### 8.1 간단한 확인 (Python)

```python
from src.rag.vector_store import VectorStore
import asyncio

async def quick_check():
    vs = VectorStore()
    count = await vs.get_count()
    print(f"벡터 DB 청크 수: {count}개")
    return count > 0

# 실행
result = asyncio.run(quick_check())
print("✅ 정상" if result else "❌ 데이터 없음")
```

### 8.2 API로 확인 (cURL)

```bash
# 인덱스 상태
curl http://localhost:8000/api/v1/admin/index/status

# 검색 테스트
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "사기", "n_results": 3}'
```

### 8.3 Swagger UI에서 확인

1. http://localhost:8000/docs 접속
2. `GET /api/v1/admin/index/status` 실행
3. `POST /api/v1/search` 실행하여 검색 테스트

---

**더 자세한 내용은 다음 문서를 참고하세요:**
- [RAG 데이터 구축 가이드](./RAG_DATA_BUILD_GUIDE.md)
- [RAG 데이터 처리 가이드](./RAG_DATA_PROCESSING_GUIDE.md)

