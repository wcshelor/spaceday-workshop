from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..main import STATE

router = APIRouter()

@router.get("/songs")
def list_songs(
    q: Optional[str] = Query(default=None, max_length=200),
    style: Optional[str] = Query(default=None),
    year_min: Optional[int] = Query(default=None, ge=1960, le=2022),
    year_max: Optional[int] = Query(default=None, ge=1960, le=2022),
    offset: int = Query(default=0, ge=0, le=10000),
    limit: int = Query(default=20, ge=1, le=100),
    sort: Optional[str] = Query(default=None),
    collaborative_only: bool = Query(default=False),
    ids: Optional[str] = Query(default=None, max_length=184),
):
    ds = STATE.get("data_store")
    if ds is None:
        raise HTTPException(status_code=503, detail="Data not ready")
    if year_min is not None and year_max is not None and year_min > year_max:
        raise HTTPException(status_code=422, detail="year_min must be <= year_max")
    recording_ids = ids.split(",") if ids else None
    if recording_ids and len(recording_ids) > 5:
        raise HTTPException(status_code=422, detail="At most 5 song IDs")
    return ds.query_songs(q=q, style=style, year_min=year_min, year_max=year_max, offset=offset, limit=limit, sort=sort, collaborative_only=collaborative_only, recording_ids=recording_ids)

@router.get("/examples")
def get_examples():
    ds = STATE.get("data_store")
    if ds is None:
        # fallback hardcoded examples
        return {"version": "prompts-v1", "items": []}
    return ds.get_examples()
