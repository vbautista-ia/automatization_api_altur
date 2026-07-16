
from fastapi import APIRouter


router = APIRouter(prefix="/report", tags=["Reporteria"])

@router.get("/transaction/by/account")
async def get_transaction_by_account():
    return "Hola mundo"
