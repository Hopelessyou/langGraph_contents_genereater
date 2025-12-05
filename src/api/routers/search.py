"""검색 API"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...rag import HybridRetriever, VectorStore, EmbeddingGenerator

router = APIRouter()

# 전역 검색기 인스턴스 (실제로는 의존성 주입 사용 권장)
_vector_store = None
_embedding_gen = None
_retriever = None


def get_retriever() -> HybridRetriever:
    """검색기 인스턴스 가져오기"""
    global _vector_store, _embedding_gen, _retriever
    
    if _retriever is None:
        _vector_store = VectorStore()
        _embedding_gen = EmbeddingGenerator()
        _retriever = HybridRetriever(_vector_store, _embedding_gen)
    
    return _retriever


class SearchRequest(BaseModel):
    """검색 요청"""
    query: str = Field(..., description="검색 쿼리")
    n_results: int = Field(default=5, ge=1, le=20, description="반환할 결과 수")
    document_types: Optional[List[str]] = Field(
        None,
        description="문서 타입 필터 (statute, case, procedure 등)"
    )
    category: Optional[str] = Field(None, description="카테고리 필터")
    sub_category: Optional[str] = Field(None, description="하위 카테고리 필터")


class SearchResult(BaseModel):
    """검색 결과 항목"""
    id: str
    document: str
    metadata: Dict[str, Any]
    distance: Optional[float] = None
    score: Optional[float] = None


class SearchResponse(BaseModel):
    """검색 응답"""
    query: str
    results: List[SearchResult]
    total: int
    timestamp: str


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    문서 검색
    
    벡터 검색을 통해 관련 법률 문서를 검색합니다.
    """
    try:
        retriever = get_retriever()
        
        # 메타데이터 필터 구성
        metadata_filters = {}
        if request.category:
            metadata_filters["category"] = request.category
        if request.sub_category:
            metadata_filters["sub_category"] = request.sub_category
        
        # 검색 수행
        search_result = retriever.search(
            query=request.query,
            n_results=request.n_results,
            document_types=request.document_types,
            metadata_filters=metadata_filters if metadata_filters else None,
        )
        
        # 결과 포맷팅
        results = [
            SearchResult(
                id=r.get("id", ""),
                document=r.get("document", ""),
                metadata=r.get("metadata", {}),
                distance=r.get("distance"),
                score=r.get("score"),
            )
            for r in search_result.get("results", [])
        ]
        
        return SearchResponse(
            query=request.query,
            results=results,
            total=len(results),
            timestamp=datetime.now().isoformat(),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"검색 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/search", response_model=SearchResponse)
async def search_documents_get(
    query: str = Query(..., description="검색 쿼리"),
    n_results: int = Query(default=5, ge=1, le=20, description="반환할 결과 수"),
    document_types: Optional[str] = Query(None, description="문서 타입 (쉼표로 구분)"),
    category: Optional[str] = Query(None, description="카테고리"),
    sub_category: Optional[str] = Query(None, description="하위 카테고리"),
):
    """GET 방식 검색"""
    # 문서 타입 파싱
    doc_types = None
    if document_types:
        doc_types = [t.strip() for t in document_types.split(",")]
    
    request = SearchRequest(
        query=query,
        n_results=n_results,
        document_types=doc_types,
        category=category,
        sub_category=sub_category,
    )
    
    return await search_documents(request)

