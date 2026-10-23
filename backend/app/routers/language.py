from fastapi import APIRouter, HTTPException
from ..schemas import TextSearchRequest, DescriptionMatchRequest
from ..main import STATE

router = APIRouter()

@router.post("/text-search")
def text_search(req: TextSearchRequest):
    ds = STATE.get("data_store")
    if ds is None:
        raise HTTPException(status_code=503, detail="Data not ready")
    if not req.query.strip():
        raise HTTPException(status_code=422, detail="query must not be empty")
    if len(req.query.strip()) > 500:
        raise HTTPException(status_code=422, detail="query too long")
    try:
        return ds.text_search(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        if "unavailable" in str(e).lower():
            raise HTTPException(status_code=503, detail=str(e))
        raise HTTPException(status_code=409, detail=str(e))

@router.post("/descriptions")
def descriptions(req: DescriptionMatchRequest):
    ds = STATE.get("data_store")
    if ds is None:
        raise HTTPException(status_code=503, detail="Data not ready")
    try:
        return ds.describe(req)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
