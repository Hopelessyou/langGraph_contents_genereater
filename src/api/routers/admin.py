"""관리자 API"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Security
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from ...rag import DocumentIndexer, IncrementalUpdater, IndexMonitor
from ...processors import BatchProcessor, QualityChecker
from ..auth import verify_api_key
from config.settings import settings

router = APIRouter()


class IndexRequest(BaseModel):
    """인덱싱 요청"""
    directory: str
    pattern: str = "*.json"
    chunk: bool = True


class IndexResponse(BaseModel):
    """인덱싱 응답"""
    success: bool
    total: int
    indexed: int
    failed: int
    details: List[Dict[str, Any]]


class IndexStatusResponse(BaseModel):
    """인덱스 상태 응답"""
    collection_name: str
    document_count: int
    indexed_documents: int
    health_status: Dict[str, Any]


@router.post("/index", response_model=IndexResponse, dependencies=[Security(verify_api_key)])
async def index_documents(request: IndexRequest):
    """
    문서 인덱싱
    
    디렉토리의 JSON 파일들을 벡터 DB에 인덱싱합니다.
    """
    try:
        indexer = DocumentIndexer()
        directory = Path(request.directory)
        
        if not directory.exists():
            raise HTTPException(
                status_code=404,
                detail=f"디렉토리가 존재하지 않습니다: {request.directory}"
            )
        
        # 인덱싱 수행
        results = indexer.index_directory(
            directory=directory,
            pattern=request.pattern,
            chunk=request.chunk,
        )
        
        return IndexResponse(
            success=True,
            total=results["total"],
            indexed=results["success"],
            failed=results["failed"],
            details=results["details"],
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"인덱싱 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/index/incremental", dependencies=[Security(verify_api_key)])
async def incremental_index(directory: str, pattern: str = "*.json"):
    """
    증분 인덱싱
    
    새로 추가되거나 변경된 문서만 인덱싱합니다.
    """
    try:
        indexer = DocumentIndexer()
        updater = IncrementalUpdater(indexer)
        
        directory_path = Path(directory)
        if not directory_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"디렉토리가 존재하지 않습니다: {directory}"
            )
        
        results = updater.update_incremental(
            directory=directory_path,
            pattern=pattern,
        )
        
        return {
            "success": True,
            "total": results["total"],
            "new": results["new"],
            "updated": results["updated"],
            "skipped": results["skipped"],
            "failed": results["failed"],
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"증분 인덱싱 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/index/status", response_model=IndexStatusResponse)
async def get_index_status():
    """인덱스 상태 조회"""
    try:
        indexer = DocumentIndexer()
        updater = IncrementalUpdater(indexer)
        monitor = IndexMonitor(indexer.vector_store, updater)
        
        status = updater.get_status()
        health = monitor.get_health_status()
        
        return IndexStatusResponse(
            collection_name=indexer.vector_store.collection_name,
            document_count=indexer.vector_store.get_count(),
            indexed_documents=status["indexed_count"],
            health_status=health,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"상태 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/index/reset", dependencies=[Security(verify_api_key)])
async def reset_index():
    """인덱스 초기화"""
    try:
        indexer = DocumentIndexer()
        indexer.vector_store.reset()
        
        return {
            "success": True,
            "message": "인덱스가 초기화되었습니다.",
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"인덱스 초기화 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/upload", dependencies=[Security(verify_api_key)])
async def upload_document(file: UploadFile = File(...)):
    """
    문서 업로드 및 인덱싱
    
    JSON 파일을 업로드하여 즉시 인덱싱합니다.
    """
    try:
        # 파일 저장
        upload_dir = Path(settings.data_dir) / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # JSON 검증
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            file_path.unlink()
            raise HTTPException(
                status_code=400,
                detail="유효하지 않은 JSON 파일입니다."
            )
        
        # 인덱싱
        indexer = DocumentIndexer()
        result = indexer.index_file(file_path)
        
        if result["success"]:
            return {
                "success": True,
                "message": "문서가 성공적으로 인덱싱되었습니다.",
                "document_id": result.get("document_id"),
                "chunks_count": result.get("chunks_count", 0),
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "알 수 없는 오류"),
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"문서 업로드 중 오류가 발생했습니다: {str(e)}"
        )

