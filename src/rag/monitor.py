"""인덱싱 상태 모니터링 도구"""

from typing import Dict, Any, List
from datetime import datetime
import logging

from .vector_store import VectorStore
from .incremental_updater import IncrementalUpdater

logger = logging.getLogger(__name__)


class IndexMonitor:
    """인덱싱 상태 모니터"""
    
    def __init__(self, vector_store: VectorStore, updater: IncrementalUpdater):
        self.vector_store = vector_store
        self.updater = updater
    
    def get_health_status(self) -> Dict[str, Any]:
        """인덱스 건강 상태를 반환합니다."""
        try:
            count = self.vector_store.get_count()
            status = self.updater.get_status()
            
            return {
                "status": "healthy" if count > 0 else "empty",
                "vector_db_count": count,
                "indexed_documents": status["indexed_count"],
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"상태 확인 실패: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """인덱스 통계를 반환합니다."""
        try:
            count = self.vector_store.get_count()
            status = self.updater.get_status()
            
            return {
                "total_chunks": count,
                "indexed_documents": status["indexed_count"],
                "average_chunks_per_document": (
                    count / status["indexed_count"] 
                    if status["indexed_count"] > 0 else 0
                ),
                "collection_name": self.vector_store.collection_name,
            }
        except Exception as e:
            logger.error(f"통계 수집 실패: {str(e)}")
            return {
                "error": str(e),
            }
    
    def check_consistency(self) -> Dict[str, Any]:
        """인덱스 일관성을 확인합니다."""
        try:
            status = self.updater.get_status()
            vector_count = self.vector_store.get_count()
            
            # 예상 청크 수 계산 (대략적)
            expected_min = status["indexed_count"]  # 최소 1개 청크/문서
            
            issues = []
            
            if vector_count < expected_min:
                issues.append(f"벡터 DB 문서 수({vector_count})가 예상보다 적습니다.")
            
            if vector_count == 0 and status["indexed_count"] > 0:
                issues.append("인덱싱 상태와 벡터 DB가 일치하지 않습니다.")
            
            return {
                "consistent": len(issues) == 0,
                "issues": issues,
                "vector_db_count": vector_count,
                "indexed_documents": status["indexed_count"],
            }
        except Exception as e:
            logger.error(f"일관성 확인 실패: {str(e)}")
            return {
                "consistent": False,
                "error": str(e),
            }

