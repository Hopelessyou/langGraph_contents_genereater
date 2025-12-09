"""API 테스트 스크립트"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api/v1"


def test_health():
    """헬스체크 테스트"""
    print("=" * 60)
    print("1. 헬스체크 테스트")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 서버 상태: {data.get('status', 'unknown')}")
            print(f"   버전: {data.get('version', 'unknown')}")
            return True
        else:
            print(f"❌ 헬스체크 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        print("   서버가 실행 중인지 확인하세요: python -m src.api.main")
        return False


def test_search(query: str, n_results: int = 5):
    """검색 API 테스트"""
    print("\n" + "=" * 60)
    print(f"2. 검색 테스트: '{query}'")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/search",
            json={
                "query": query,
                "n_results": n_results,
                "document_types": ["statute", "case"]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            print(f"✅ 검색 성공: {len(results)}개 결과")
            
            for i, result in enumerate(results[:3], 1):  # 상위 3개만 출력
                # SearchResult 구조: id, document, metadata, distance, score
                metadata = result.get('metadata', {}) if isinstance(result.get('metadata'), dict) else {}
                title = metadata.get('title', 'N/A')
                doc_type = metadata.get('type', 'N/A')
                category = metadata.get('category', 'N/A')
                
                # score 또는 distance 사용 (distance는 작을수록 유사, score는 클수록 유사)
                score = result.get('score')
                distance = result.get('distance')
                similarity = score if score is not None else (1 - distance if distance is not None else None)
                
                print(f"\n[{i}] {title}")
                print(f"    ID: {result.get('id', 'N/A')}")
                print(f"    타입: {doc_type}")
                print(f"    카테고리: {category}")
                if similarity is not None:
                    try:
                        print(f"    유사도: {similarity:.4f}")
                    except (TypeError, ValueError):
                        print(f"    유사도: {similarity}")
                
                # document 필드에서 내용 가져오기
                content = result.get('document', '')
                if content:
                    content_preview = content[:150] if isinstance(content, str) else str(content)[:150]
                    print(f"    내용: {content_preview}...")
                else:
                    print(f"    내용: (없음)")
            
            return True
        else:
            print(f"❌ 검색 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 검색 오류: {e}")
        return False


def test_ask(query: str):
    """질의응답 API 테스트"""
    print("\n" + "=" * 60)
    print(f"3. 질의응답 테스트: '{query}'")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json={
                "query": query,
                "n_results": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "")
            sources = data.get("sources", [])
            
            print(f"✅ 질의응답 성공")
            print(f"\n답변:")
            print(f"{answer[:500]}..." if len(answer) > 500 else answer)
            
            if sources:
                print(f"\n출처 ({len(sources)}개):")
                for i, source in enumerate(sources[:3], 1):
                    print(f"  [{i}] {source.get('title', 'N/A')}")
            
            return True
        else:
            print(f"❌ 질의응답 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 질의응답 오류: {e}")
        return False


def test_index_status():
    """인덱스 상태 확인"""
    print("\n" + "=" * 60)
    print("4. 인덱스 상태 확인")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/admin/index/status")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 인덱스 상태 확인 성공")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"⚠️  인덱스 상태 확인 실패: {response.status_code}")
            print("   (API 키가 필요할 수 있습니다)")
            return False
    except Exception as e:
        print(f"⚠️  인덱스 상태 확인 오류: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("\n" + "=" * 60)
    print("IBS 법률 AI 시스템 API 테스트")
    print("=" * 60)
    
    # 1. 헬스체크
    if not test_health():
        print("\n❌ 서버가 실행되지 않았습니다.")
        print("   다음 명령으로 서버를 실행하세요:")
        print("   python -m src.api.main")
        return
    
    # 2. 검색 테스트
    test_queries = [
        "사기죄 처벌",
        "집행유예 조건",
        "형법 제347조"
    ]
    
    for query in test_queries:
        test_search(query, n_results=3)
    
    # 3. 질의응답 테스트
    test_ask("사기 초범은 집행유예가 가능한가요?")
    
    # 4. 인덱스 상태 확인
    test_index_status()
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)
    print("\n💡 추가 테스트:")
    print("   - 브라우저에서 http://localhost:8000/docs 접속")
    print("   - Swagger UI에서 직접 API 테스트 가능")


if __name__ == "__main__":
    main()

