from fastapi import APIRouter
from src.pipelines.nkod_query_matcher_pipeline import NkodQueryMatcherPipeline
from src.schemas.nkod_query_matcher_request import NkodQueryMatcherRequest
from src.schemas.nkod_query_matcher_response import NkodQueryMatcherResponse


router = APIRouter()

@router.post("/match-query", response_model=NkodQueryMatcherResponse)
async def match_query(request: NkodQueryMatcherRequest):
    return NkodQueryMatcherPipeline().run(request)
