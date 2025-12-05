"""모니터링 시스템"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class APIMonitor:
    """API 사용량 모니터"""
    
    def __init__(self):
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.response_times: Dict[str, List[float]] = defaultdict(list)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.start_time = datetime.now()
    
    def record_request(
        self,
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int,
    ):
        """
        API 요청을 기록합니다.
        
        Args:
            endpoint: 엔드포인트
            method: HTTP 메서드
            response_time: 응답 시간
            status_code: HTTP 상태 코드
        """
        key = f"{method} {endpoint}"
        self.request_counts[key] += 1
        self.response_times[key].append(response_time)
        
        if status_code >= 400:
            self.error_counts[key] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계를 반환합니다."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        stats = {
            "uptime_seconds": uptime,
            "total_requests": sum(self.request_counts.values()),
            "endpoints": {},
        }
        
        for endpoint, count in self.request_counts.items():
            times = self.response_times.get(endpoint, [])
            avg_time = sum(times) / len(times) if times else 0
            max_time = max(times) if times else 0
            min_time = min(times) if times else 0
            
            stats["endpoints"][endpoint] = {
                "request_count": count,
                "error_count": self.error_counts.get(endpoint, 0),
                "avg_response_time": avg_time,
                "max_response_time": max_time,
                "min_response_time": min_time,
            }
        
        return stats


class PerformanceMetrics:
    """성능 메트릭 수집"""
    
    def __init__(self):
        self.search_metrics: List[Dict[str, Any]] = []
        self.llm_metrics: List[Dict[str, Any]] = []
        self.vector_db_metrics: List[Dict[str, Any]] = []
    
    def record_search(
        self,
        query: str,
        results_count: int,
        response_time: float,
    ):
        """검색 메트릭 기록"""
        self.search_metrics.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results_count": results_count,
            "response_time": response_time,
        })
        
        # 최근 1000개만 유지
        if len(self.search_metrics) > 1000:
            self.search_metrics = self.search_metrics[-1000:]
    
    def record_llm_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        response_time: float,
    ):
        """LLM 사용량 기록"""
        self.llm_metrics.append({
            "timestamp": datetime.now().isoformat(),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "response_time": response_time,
        })
        
        if len(self.llm_metrics) > 1000:
            self.llm_metrics = self.llm_metrics[-1000:]
    
    def get_search_stats(self, hours: int = 24) -> Dict[str, Any]:
        """검색 통계 반환"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.search_metrics
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]
        
        if not recent_metrics:
            return {"total": 0}
        
        response_times = [m["response_time"] for m in recent_metrics]
        
        return {
            "total": len(recent_metrics),
            "avg_response_time": sum(response_times) / len(response_times),
            "max_response_time": max(response_times),
            "min_response_time": min(response_times),
        }
    
    def get_llm_stats(self, hours: int = 24) -> Dict[str, Any]:
        """LLM 통계 반환"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.llm_metrics
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]
        
        if not recent_metrics:
            return {"total": 0}
        
        total_tokens = sum(m["total_tokens"] for m in recent_metrics)
        total_prompt = sum(m["prompt_tokens"] for m in recent_metrics)
        total_completion = sum(m["completion_tokens"] for m in recent_metrics)
        
        return {
            "total_requests": len(recent_metrics),
            "total_tokens": total_tokens,
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "avg_tokens_per_request": total_tokens / len(recent_metrics),
        }


class VectorDBMonitor:
    """벡터 DB 상태 모니터링"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.last_check = None
        self.status_history: List[Dict[str, Any]] = []
    
    def check_status(self) -> Dict[str, Any]:
        """벡터 DB 상태 확인"""
        try:
            count = self.vector_store.get_count()
            status = {
                "timestamp": datetime.now().isoformat(),
                "status": "healthy",
                "document_count": count,
                "collection_name": self.vector_store.collection_name,
            }
        except Exception as e:
            status = {
                "timestamp": datetime.now().isoformat(),
                "status": "unhealthy",
                "error": str(e),
            }
        
        self.status_history.append(status)
        self.last_check = datetime.now()
        
        # 최근 100개만 유지
        if len(self.status_history) > 100:
            self.status_history = self.status_history[-100:]
        
        return status
    
    def get_status_summary(self) -> Dict[str, Any]:
        """상태 요약 반환"""
        if not self.status_history:
            return {"status": "unknown"}
        
        recent_statuses = self.status_history[-10:]  # 최근 10개
        healthy_count = sum(1 for s in recent_statuses if s.get("status") == "healthy")
        
        return {
            "current_status": recent_statuses[-1].get("status", "unknown"),
            "health_rate": healthy_count / len(recent_statuses) if recent_statuses else 0,
            "last_check": self.last_check.isoformat() if self.last_check else None,
        }

