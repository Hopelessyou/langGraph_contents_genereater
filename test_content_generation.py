"""법률 콘텐츠 생성 API 테스트"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_generate_blog():
    """블로그 포스팅 생성 테스트"""
    print("=" * 60)
    print("법률 블로그 포스팅 생성 테스트")
    print("=" * 60)
    
    response = requests.post(
        f"{BASE_URL}/generate",
        json={
            "topic": "사기죄 처벌과 집행유예",
            "content_type": "blog",
            "target_length": 2000,
            "keywords": ["사기죄", "집행유예", "초범"],
            "include_sections": ["법적기준", "판례", "대응방법"],
            "document_types": ["statute", "case"],
            "n_references": 5
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 콘텐츠 생성 성공!")
        print(f"\n제목: {data.get('title', 'N/A')}")
        print(f"\n생성된 콘텐츠:")
        print("-" * 60)
        content = data.get('content', '')
        print(content[:1000] + "..." if len(content) > 1000 else content)
        print("-" * 60)
        
        if data.get('sections'):
            print(f"\n섹션:")
            for section, content in data['sections'].items():
                print(f"  - {section}: {len(content)}자")
        
        print(f"\n참고 문서 ({len(data.get('references', []))}개):")
        for i, ref in enumerate(data.get('references', [])[:3], 1):
            print(f"  [{i}] {ref.get('title', 'N/A')} ({ref.get('type', 'N/A')})")
        
        print(f"\n메타데이터:")
        print(f"  - 글자 수: {data.get('metadata', {}).get('word_count', 'N/A')}")
        print(f"  - 콘텐츠 타입: {data.get('metadata', {}).get('content_type', 'N/A')}")
        
        return True
    else:
        print(f"❌ 생성 실패: {response.status_code}")
        print(f"   응답: {response.text}")
        return False


def test_generate_article():
    """법률 기사 생성 테스트"""
    print("\n" + "=" * 60)
    print("법률 기사 생성 테스트")
    print("=" * 60)
    
    response = requests.post(
        f"{BASE_URL}/generate",
        json={
            "topic": "형법 제347조 사기죄",
            "content_type": "article",
            "style": "전문적이고 객관적",
            "document_types": ["statute"],
            "n_references": 3
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 기사 생성 성공!")
        print(f"\n제목: {data.get('title', 'N/A')}")
        print(f"\n내용 미리보기:")
        content = data.get('content', '')
        print(content[:500] + "..." if len(content) > 500 else content)
        return True
    else:
        print(f"❌ 생성 실패: {response.status_code}")
        return False


def test_generate_faq():
    """FAQ 생성 테스트"""
    print("\n" + "=" * 60)
    print("FAQ 생성 테스트")
    print("=" * 60)
    
    response = requests.post(
        f"{BASE_URL}/generate",
        json={
            "topic": "사기죄",
            "content_type": "faq",
            "document_types": ["statute", "case"],
            "n_references": 5
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ FAQ 생성 성공!")
        print(f"\n생성된 FAQ:")
        print("-" * 60)
        content = data.get('content', '')
        print(content)
        print("-" * 60)
        return True
    else:
        print(f"❌ 생성 실패: {response.status_code}")
        return False


def main():
    """메인 테스트 함수"""
    print("\n" + "=" * 60)
    print("법률 콘텐츠 생성 API 테스트")
    print("=" * 60)
    
    # 1. 블로그 포스팅 생성
    test_generate_blog()
    
    # 2. 법률 기사 생성
    # test_generate_article()
    
    # 3. FAQ 생성
    # test_generate_faq()
    
    print("\n" + "=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)
    print("\n💡 추가 테스트:")
    print("   - 브라우저에서 http://localhost:8000/docs 접속")
    print("   - POST /api/v1/generate 엔드포인트에서 직접 테스트 가능")


if __name__ == "__main__":
    main()

