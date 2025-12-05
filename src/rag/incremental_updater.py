"""증분 업데이트 로직"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import logging

from .indexer import DocumentIndexer
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class IncrementalUpdater:
    """증분 업데이트 관리자"""
    
    def __init__(
        self,
        indexer: DocumentIndexer,
        state_file: Path | str = "./data/index_state.json",
    ):
        self.indexer = indexer
        self.vector_store = indexer.vector_store
        self.state_file = Path(state_file)
        self.indexed_ids: Set[str] = set()
        self._load_state()
    
    def _load_state(self):
        """인덱싱 상태를 로드합니다."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    self.indexed_ids = set(state.get("indexed_ids", []))
                logger.info(f"인덱싱 상태 로드: {len(self.indexed_ids)}개 문서")
            except Exception as e:
                logger.warning(f"상태 파일 로드 실패: {str(e)}")
                self.indexed_ids = set()
        else:
            self.indexed_ids = set()
    
    def _save_state(self):
        """인덱싱 상태를 저장합니다."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            state = {
                "indexed_ids": list(self.indexed_ids),
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.debug(f"인덱싱 상태 저장: {len(self.indexed_ids)}개 문서")
        except Exception as e:
            logger.error(f"상태 파일 저장 실패: {str(e)}")
    
    def is_indexed(self, document_id: str) -> bool:
        """문서가 이미 인덱싱되었는지 확인합니다."""
        return document_id in self.indexed_ids
    
    def update_incremental(
        self,
        directory: Path | str,
        pattern: str = "*.json",
        force_update: bool = False,
    ) -> Dict[str, Any]:
        """
        증분 업데이트를 수행합니다.
        
        Args:
            directory: 디렉토리 경로
            pattern: 파일 패턴
            force_update: 강제 업데이트 여부 (기존 문서도 다시 인덱싱)
            
        Returns:
            업데이트 결과
        """
        directory = Path(directory)
        results = {
            "total": 0,
            "new": 0,
            "updated": 0,
            "skipped": 0,
            "failed": 0,
            "details": [],
        }
        
        for file_path in directory.glob(pattern):
            results["total"] += 1
            
            try:
                # JSON 파일에서 ID 추출
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    document_id = data.get("id", file_path.stem)
                
                # 이미 인덱싱된 경우
                if self.is_indexed(document_id) and not force_update:
                    results["skipped"] += 1
                    results["details"].append({
                        "file": file_path.name,
                        "status": "skipped",
                        "reason": "already_indexed",
                    })
                    continue
                
                # 인덱싱 수행
                result = self.indexer.index_file(file_path)
                
                if result["success"]:
                    # 상태 업데이트
                    if self.is_indexed(document_id):
                        results["updated"] += 1
                        status = "updated"
                    else:
                        results["new"] += 1
                        status = "new"
                    
                    self.indexed_ids.add(document_id)
                    results["details"].append({
                        "file": file_path.name,
                        "status": status,
                        "chunks_count": result.get("chunks_count", 0),
                    })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "file": file_path.name,
                        "status": "failed",
                        "error": result.get("error", "unknown"),
                    })
                    
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "file": file_path.name,
                    "status": "failed",
                    "error": str(e),
                })
                logger.error(f"파일 처리 실패: {file_path} - {str(e)}")
        
        # 상태 저장
        self._save_state()
        
        logger.info(
            f"증분 업데이트 완료: 총 {results['total']}건, "
            f"신규 {results['new']}건, 업데이트 {results['updated']}건, "
            f"건너뜀 {results['skipped']}건, 실패 {results['failed']}건"
        )
        
        return results
    
    def remove_document(self, document_id: str):
        """문서를 인덱스에서 제거합니다."""
        # 벡터 DB에서 삭제 (청크 포함)
        self.vector_store.delete(where={"document_id": document_id})
        
        # 상태에서 제거
        self.indexed_ids.discard(document_id)
        self._save_state()
        
        logger.info(f"문서 제거 완료: {document_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """현재 상태를 반환합니다."""
        return {
            "indexed_count": len(self.indexed_ids),
            "indexed_ids": list(self.indexed_ids),
            "vector_db_count": self.vector_store.get_count(),
        }

