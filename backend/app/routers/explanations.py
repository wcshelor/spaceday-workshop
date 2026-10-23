from fastapi import APIRouter, HTTPException
from ..schemas import ExplanationRequest
from ..main import STATE

router = APIRouter()

@router.post("/explanations")
def explanations(req: ExplanationRequest):
    ds = STATE.get("data_store")
    if ds is None:
        raise HTTPException(status_code=503, detail="Data not ready")
    try:
        return ds.explain(req)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
