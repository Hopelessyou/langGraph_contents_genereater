"""쿼리 캐싱 모듈"""

from typing import Dict, Any, Optional
import time
import hashlib
import json
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)


class QueryCache:
    """쿼리 결과 캐싱 클래스"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        캐시 초기화
        
        Args:
            max_size: 최대 캐시 항목 수
            ttl: Time To Live (초 단위, 기본값: 1시간)
        """
        self.max_size = max_size
        self.ttl = ttl
        # OrderedDict를 사용하여 LRU 캐시 구현
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._hits = 0
        self._misses = 0
    
    def _generate_key(self, query: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        쿼리와 필터로부터 캐시 키 생성
        
        Args:
            query: 검색 쿼리
            filters: 메타데이터 필터
            
        Returns:
            캐시 키 (해시값)
        """
        # 쿼리와 필터를 JSON으로 직렬화하여 해시 생성
        cache_data = {
            "query": query,
            "filters": filters or {},
        }
        cache_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(cache_str.encode('utf-8')).hexdigest()
    
    def get(self, query: str, filters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        캐시에서 결과 가져오기
        
        Args:
            query: 검색 쿼리
            filters: 메타데이터 필터
            
        Returns:
            캐시된 결과 또는 None
        """
        key = self._generate_key(query, filters)
        
        if key not in self._cache:
            self._misses += 1
            return None
        
        cache_entry = self._cache[key]
        
        # TTL 확인
        if time.time() - cache_entry["timestamp"] > self.ttl:
            # 만료된 항목 제거
            del self._cache[key]
            self._misses += 1
            logger.debug(f"캐시 만료: {query[:50]}...")
            return None
        
        # LRU: 사용된 항목을 맨 뒤로 이동
        self._cache.move_to_end(key)
        self._hits += 1
        logger.debug(f"캐시 히트: {query[:50]}...")
        
        return cache_entry["result"]
    
    def set(
        self,
        query: str,
        result: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
    ):
        """
        캐시에 결과 저장
        
        Args:
            query: 검색 쿼리
            result: 검색 결과
            filters: 메타데이터 필터
        """
        key = self._generate_key(query, filters)
        
        # 최대 크기 확인
        if len(self._cache) >= self.max_size:
            # 가장 오래된 항목 제거 (FIFO)
            self._cache.popitem(last=False)
            logger.debug("캐시 크기 제한으로 인한 항목 제거")
        
        # 캐시에 저장
        self._cache[key] = {
            "result": result,
            "timestamp": time.time(),
            "query": query,  # 디버깅용
        }
        
        # LRU: 새 항목을 맨 뒤로 이동
        self._cache.move_to_end(key)
        logger.debug(f"캐시 저장: {query[:50]}...")
    
    def clear(self):
        """캐시 전체 삭제"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("캐시 전체 삭제 완료")
    
    def invalidate(self, query: str, filters: Optional[Dict[str, Any]] = None):
        """
        특정 쿼리의 캐시 무효화
        
        Args:
            query: 검색 쿼리
            filters: 메타데이터 필터
        """
        key = self._generate_key(query, filters)
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"캐시 무효화: {query[:50]}...")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        캐시 통계 반환
        
        Returns:
            캐시 통계 딕셔너리
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
            "ttl": self.ttl,
        }
    
    def cleanup_expired(self):
        """만료된 항목 제거"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time - entry["timestamp"] > self.ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"{len(expired_keys)}개 만료된 캐시 항목 제거")

