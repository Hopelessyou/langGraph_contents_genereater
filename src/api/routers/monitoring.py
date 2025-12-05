"""모니터링 API"""

from fastapi import APIRouter, Security
from pydantic import BaseModel
from typing import Dict, Any

from ..auth import verify_api_key
from ...utils.monitoring import APIMonitor, PerformanceMetrics, VectorDBMonitor
from ...rag import VectorStore

router = APIRouter()

# 전역 모니터 인스턴스
api_monitor = APIMonitor()
performance_metrics = PerformanceMetrics()


@router.get("/monitoring/stats")
async def get_monitoring_stats() -> Dict[str, Any]:
    """모니터링 통계 조회"""
    api_stats = api_monitor.get_statistics()
    search_stats = performance_metrics.get_search_stats()
    llm_stats = performance_metrics.get_llm_stats()
    
    return {
        "api": api_stats,
        "search": search_stats,
        "llm": llm_stats,
    }


@router.get("/monitoring/vector-db", dependencies=[Security(verify_api_key)])
async def get_vector_db_status() -> Dict[str, Any]:
    """벡터 DB 상태 조회"""
    try:
        vector_store = VectorStore()
        monitor = VectorDBMonitor(vector_store)
        status = monitor.check_status()
        summary = monitor.get_status_summary()
        
        return {
            "current_status": status,
            "summary": summary,
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "unavailable",
        }

