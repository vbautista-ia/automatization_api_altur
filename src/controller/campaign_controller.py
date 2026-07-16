from fastapi import APIRouter


router = APIRouter()

@router.get("/campaign")
async def get_all_campaigns():
    return ["campaign 1", "campaign 2", "campaign 3"]