from fastapi import APIRouter, Request


router = APIRouter()

@router.post("/update-nkod-data")
async def add_relevant_queries(request: Request):
    pass