#!/usr/bin/env python3
"""인덱싱된 데이터 확인 스크립트"""

import sys
from pathlib import Path
import asyncio
import logging

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.rag.vector_store import VectorStore
from src.rag.embedding import EmbeddingGenerator
from src.rag.retriever import HybridRetriever
from src.rag.indexer import DocumentIndexer
from src.rag.incremental_updater import IncrementalUpdater
from config.settings import settings

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)


async def check_indexed_data():
    """인덱싱된 데이터 종합 확인"""
    
    print("=" * 60)
    print("📊 인덱싱 데이터 확인")
    print("=" * 60)
    
    # 1. 벡터 DB 상태 확인
    print("\n1️⃣ 벡터 DB 상태")
    print("-" * 60)
    try:
        vector_store = VectorStore(collection_name="legal_documents")
        count = vector_store.get_count()  # 동기 메서드
        print(f"   ✅ 벡터 DB 청크 수: {count}개")
        print(f"   컬렉션 이름: {vector_store.collection_name}")
        
        if count == 0:
            print("\n⚠️  벡터 DB가 비어있습니다!")
            print("   데이터를 인덱싱하세요:")
            print("   python scripts/process_and_index.py --input-dir data/processed/statutes --doc-type statute")
            print("   python scripts/process_and_index.py --input-dir data/processed/cases --doc-type case")
            return False
    except Exception as e:
        print(f"   ❌ 벡터 DB 확인 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. 인덱싱 상태 확인
    print("\n2️⃣ 인덱싱 상태")
    print("-" * 60)
    try:
        embedding_gen = EmbeddingGenerator()
        indexer = DocumentIndexer(collection_name="legal_documents")
        updater = IncrementalUpdater(
            indexer=indexer,
            state_file=Path("./data/index_state.json")
        )
        
        status = updater.get_status()
        print(f"   인덱싱된 문서 수: {status['indexed_count']}개")
        print(f"   마지막 업데이트: {status.get('last_updated', 'N/A')}")
    except Exception as e:
        print(f"   ⚠️  인덱싱 상태 확인 실패: {e}")
        # 상태 파일이 없어도 계속 진행
    
    # 3. 검색 테스트
    print("\n3️⃣ 검색 테스트")
    print("-" * 60)
    try:
        retriever = HybridRetriever(vector_store, embedding_gen)
        test_query = "사기"
        
        print(f"   테스트 쿼리: '{test_query}'")
        search_results = await retriever.search(
            query=test_query,
            n_results=5
        )
        
        if search_results.get('results') and len(search_results['results']) > 0:
            print(f"   ✅ 검색 성공: {len(search_results['results'])}개 결과")
            print("\n   검색 결과 (상위 3개):")
            for i, result in enumerate(search_results['results'][:3], 1):
                print(f"   {i}. ID: {result.get('id', 'N/A')}")
                metadata = result.get('metadata', {})
                print(f"      제목: {metadata.get('title', 'N/A')}")
                print(f"      타입: {metadata.get('type', 'N/A')}")
                print(f"      거리: {result.get('distance', 'N/A'):.4f}")
                doc_preview = result.get('document', '')[:50]
                print(f"      내용: {doc_preview}...")
        else:
            print(f"   ❌ 검색 실패: 결과 없음")
            print("   ⚠️  데이터가 인덱싱되지 않았거나, 검색 쿼리와 일치하는 문서가 없습니다.")
    except Exception as e:
        print(f"   ⚠️  검색 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. 문서 타입별 통계
    print("\n4️⃣ 문서 타입별 통계")
    print("-" * 60)
    try:
        import chromadb
        from chromadb.config import Settings
        
        client = chromadb.PersistentClient(
            path=str(Path("./data/vector_db")),
            settings=Settings(anonymized_telemetry=False)
        )
        collection = client.get_collection(vector_store.collection_name)
        
        # 샘플 데이터 가져오기 (메타데이터만)
        sample_data = collection.get(limit=1000)  # 더 많은 샘플
        
        if sample_data.get('metadatas'):
            type_counts = {}
            for metadata in sample_data['metadatas']:
                doc_type = metadata.get('type', 'unknown')
                type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
            
            if type_counts:
                for doc_type, count in sorted(type_counts.items()):
                    print(f"   {doc_type}: {count}개 청크 (샘플)")
            else:
                print("   통계 수집 불가")
        else:
            print("   메타데이터 없음")
    except Exception as e:
        print(f"   ⚠️  통계 수집 실패: {e}")
    
    print("\n" + "=" * 60)
    if count > 0:
        print("✅ 데이터가 인덱싱되어 있습니다!")
    else:
        print("❌ 데이터가 인덱싱되지 않았습니다.")
    print("=" * 60)
    
    return count > 0


if __name__ == "__main__":
    asyncio.run(check_indexed_data())

