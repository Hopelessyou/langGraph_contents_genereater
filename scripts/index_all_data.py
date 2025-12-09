#!/usr/bin/env python3
"""
data 폴더의 모든 파일을 인덱싱하는 스크립트
"""

import sys
from pathlib import Path
import asyncio
import logging

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.indexer import DocumentIndexer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def index_all_data():
    """data 폴더의 모든 파일을 인덱싱"""
    
    print("=" * 80)
    print("전체 데이터 인덱싱 시작")
    print("=" * 80)
    
    # 인덱서 생성
    indexer = DocumentIndexer()
    
    # 인덱싱할 디렉토리 목록
    directories = [
        {
            "path": project_root / "data" / "processed",
            "name": "처리된 데이터 (processed)",
            "pattern": "*.json",
            "recursive": True
        },
        {
            "path": project_root / "data" / "collected",
            "name": "수집된 데이터 (collected)",
            "pattern": "*.json",
            "recursive": True
        }
    ]
    
    total_stats = {
        "total_files": 0,
        "total_success": 0,
        "total_failed": 0,
        "total_chunks": 0
    }
    
    # 각 디렉토리 인덱싱
    for dir_info in directories:
        dir_path = dir_info["path"]
        
        if not dir_path.exists():
            logger.warning(f"디렉토리가 존재하지 않습니다: {dir_path}")
            continue
        
        print("\n" + "=" * 80)
        print(f"인덱싱 중: {dir_info['name']}")
        print(f"경로: {dir_path}")
        print("=" * 80)
        
        try:
            # 디렉토리 인덱싱
            results = indexer.index_directory(
                directory=dir_path,
                pattern=dir_info["pattern"],
                chunk=True,
                recursive=dir_info["recursive"]
            )
            
            # 통계 업데이트
            total_stats["total_files"] += results["total"]
            total_stats["total_success"] += results["success"]
            total_stats["total_failed"] += results["failed"]
            
            # 청크 수 계산
            chunks = sum(
                detail.get("result", {}).get("chunks_count", 0)
                for detail in results.get("details", [])
                if detail.get("result", {}).get("success", False)
            )
            total_stats["total_chunks"] += chunks
            
            # 결과 출력
            print(f"\n✅ {dir_info['name']} 인덱싱 완료:")
            print(f"   총 파일: {results['total']}개")
            print(f"   성공: {results['success']}개")
            print(f"   실패: {results['failed']}개")
            print(f"   청크 수: {chunks}개")
            
            # 실패한 파일 목록 출력
            if results["failed"] > 0:
                print(f"\n❌ 실패한 파일:")
                for detail in results["details"]:
                    if not detail.get("result", {}).get("success", False):
                        file_path = detail.get("file", "unknown")
                        error = detail.get("result", {}).get("error", "알 수 없는 오류")
                        print(f"   - {file_path}: {error}")
        
        except Exception as e:
            logger.error(f"{dir_info['name']} 인덱싱 중 오류 발생: {str(e)}")
            print(f"\n❌ {dir_info['name']} 인덱싱 실패: {str(e)}")
    
    # 전체 통계 출력
    print("\n" + "=" * 80)
    print("전체 인덱싱 완료")
    print("=" * 80)
    print(f"총 파일 수: {total_stats['total_files']}개")
    print(f"성공: {total_stats['total_success']}개")
    print(f"실패: {total_stats['total_failed']}개")
    print(f"총 청크 수: {total_stats['total_chunks']}개")
    print("=" * 80)
    
    # 인덱스 상태 확인
    try:
        status = indexer.get_index_status()
        print(f"\n인덱스 상태:")
        print(f"  총 문서 수: {status.get('total_documents', 0)}개")
        print(f"  총 청크 수: {status.get('total_chunks', 0)}개")
    except Exception as e:
        logger.warning(f"인덱스 상태 확인 실패: {str(e)}")


if __name__ == "__main__":
    try:
        asyncio.run(index_all_data())
    except KeyboardInterrupt:
        print("\n\n인덱싱이 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"인덱싱 중 오류 발생: {str(e)}")
        sys.exit(1)

