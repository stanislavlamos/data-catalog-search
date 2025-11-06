from fastapi import APIRouter
from src.pipelines.nkod_openai_files_pipeline import NkodOpenAiFilesPipeline
from src.schemas.nkod_openai_files_request import NkodOpenAiFilesRequest
from src.schemas.nkod_openai_files_response import NkodOpenAiFilesResponse 


router = APIRouter()

@router.post("/nkod-openai-files", response_model=NkodOpenAiFilesResponse)
async def nkod_rag(request: NkodOpenAiFilesRequest):
    return NkodOpenAiFilesPipeline(request).run()