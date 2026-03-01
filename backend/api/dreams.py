from fastapi import APIRouter

router = APIRouter()


@router.post("/dreams")
async def create_dream():
    return {"message": "placeholder"}


@router.get("/dreams")
async def list_dreams():
    return {"dreams": []}


@router.get("/dreams/{dream_id}")
async def get_dream(dream_id: str):
    return {"dream_id": dream_id}


@router.get("/dreams/{dream_id}/status")
async def get_dream_status(dream_id: str):
    return {"dream_id": dream_id, "status": "pending"}


@router.delete("/dreams/{dream_id}")
async def delete_dream(dream_id: str):
    return {"deleted": dream_id}
