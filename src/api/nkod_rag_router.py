from fastapi import APIRouter
from src.pipelines.nkod_rag_pipeline import NkodRagPipeline
from src.schemas.nkod_rag_request import NkodRagRequest
from src.schemas.nkod_rag_response import NkodRagResponse


router = APIRouter()

@router.post("/nkod-rag", response_model=NkodRagResponse)
async def nkod_rag(request: NkodRagRequest):
    return NkodRagPipeline(request).run()