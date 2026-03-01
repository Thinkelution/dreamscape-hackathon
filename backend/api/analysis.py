from fastapi import APIRouter

router = APIRouter()


@router.get("/analysis")
async def get_analysis():
    return {"analysis": None}


@router.post("/analysis/refresh")
async def refresh_analysis():
    return {"message": "placeholder"}
