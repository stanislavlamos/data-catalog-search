from fastapi import APIRouter
from src.pipelines.nkod_shacl_pipeline import NkodShaclPipeline
from src.schemas.nkod_shacl_request import NkodShaclRequest
from src.schemas.nkod_shacl_response import NkodShaclResponse 


router = APIRouter()

@router.post("/nkod-shacl", response_model=NkodShaclResponse)
async def nkod_shacl(request: NkodShaclRequest):
    return NkodShaclPipeline(request).run()