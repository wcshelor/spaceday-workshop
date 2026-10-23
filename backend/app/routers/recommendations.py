from fastapi import APIRouter, HTTPException, Request
import hashlib
import uuid
from ..schemas import RecommendationRequest, RecommendationResponse
from ..main import STATE

router = APIRouter()

@router.post("/recommendations", response_model=RecommendationResponse)
def recommend(req: RecommendationRequest, request: Request):
    ds = STATE.get("data_store")
    if ds is None:
        raise HTTPException(status_code=503, detail="Data not ready")
    # validation
    if len(set(req.seed_ids)) != len(req.seed_ids):
        raise HTTPException(status_code=422, detail="duplicate seed_ids")
    if req.candidate_filter:
        ym = req.candidate_filter.get("year_min")
        yx = req.candidate_filter.get("year_max")
        if ym is not None and yx is not None and ym > yx:
            raise HTTPException(status_code=422, detail="year_min must be <= year_max")
    try:
        result = ds.recommend(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return result
