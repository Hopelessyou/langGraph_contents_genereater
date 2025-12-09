#!/usr/bin/env python3
"""인덱싱된 데이터 확인 스크립트"""

import sys
from pathlib import Path
import asyncio

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.rag import DocumentIndexer, VectorStore, EmbeddingGenerator
from src.rag.incremental_updater import IncrementalUpdater
from src.rag.monitor import IndexMonitor


async def check_indexed_data():
    """인덱싱된 데이터 종합 확인"""
    
    print("=" * 60)
    print("📊 인덱싱 데이터 확인")
    print("=" * 60)
    
    # 1. 벡터 DB 상태 확인
    print("\n1️⃣ 벡터 DB 상태")
    print("-" * 60)
    try:
        vector_store = VectorStore()
        count = await vector_store.get_count()
        print(f"   벡터 DB 청크 수: {count}개")
        print(f"   컬렉션 이름: {vector_store.collection_name}")
        
        if count == 0:
            print("\n⚠️  벡터 DB가 비어있습니다!")
            print("   데이터를 인덱싱하세요:")
            print("   python scripts/process_and_index.py --input-dir data/processed/cases --doc-type case")
            return
    except Exception as e:
        print(f"   ❌ 벡터 DB 확인 실패: {e}")
        return
    
    # 2. 인덱싱 상태 확인
    print("\n2️⃣ 인덱싱 상태")
    print("-" * 60)
    try:
        indexer = DocumentIndexer()
        updater = IncrementalUpdater(indexer)
        monitor = IndexMonitor(indexer.vector_store, updater)
        
        status = updater.get_status()
        health = monitor.get_health_status()
        
        print(f"   인덱싱된 문서 수: {status['indexed_count']}개")
        print(f"   벡터 DB 청크 수: {health['vector_db_count']}개")
        print(f"   상태: {health['status']}")
        
        # 통계
        statistics = monitor.get_statistics()
        if statistics.get('average_chunks_per_document'):
            print(f"   문서당 평균 청크 수: {statistics['average_chunks_per_document']:.1f}개")
    except Exception as e:
        print(f"   ⚠️  인덱싱 상태 확인 실패: {e}")
    
    # 3. 일관성 확인
    print("\n3️⃣ 일관성 확인")
    print("-" * 60)
    try:
        consistency = monitor.check_consistency()
        if consistency['consistent']:
            print("   ✅ 인덱스 일관성: 정상")
        else:
            print("   ❌ 인덱스 일관성: 문제 발견")
            for issue in consistency.get('issues', []):
                print(f"      - {issue}")
    except Exception as e:
        print(f"   ⚠️  일관성 확인 실패: {e}")
    
    # 4. 검색 테스트
    print("\n4️⃣ 검색 테스트")
    print("-" * 60)
    try:
        embedding_gen = EmbeddingGenerator()
        test_query = "사기 범죄"
        
        print(f"   테스트 쿼리: '{test_query}'")
        query_embedding = await embedding_gen.embed_text(test_query)
        results = await vector_store.search(
            query_embedding=query_embedding,
            n_results=3
        )
        
        if results.get('ids') and len(results['ids'][0]) > 0:
            print(f"   ✅ 검색 성공: {len(results['ids'][0])}개 결과")
            print("\n   검색 결과:")
            for i, doc_id in enumerate(results['ids'][0][:3], 1):
                print(f"   {i}. {doc_id}")
                if results.get('metadatas') and results['metadatas'][0]:
                    metadata = results['metadatas'][0][i-1]
                    print(f"      제목: {metadata.get('title', 'N/A')}")
                    print(f"      타입: {metadata.get('type', 'N/A')}")
        else:
            print(f"   ❌ 검색 실패: 결과 없음")
    except Exception as e:
        print(f"   ⚠️  검색 테스트 실패: {e}")
    
    # 5. 문서 타입별 통계
    print("\n5️⃣ 문서 타입별 통계")
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
        sample_data = collection.get(limit=100)
        
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
    except Exception as e:
        print(f"   ⚠️  통계 수집 실패: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 확인 완료!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(check_indexed_data())

