from fastapi import APIRouter
from src.pipelines.language_detection_pipeline import LanguageDetectionPipeline
from src.schemas.language_detection_request import LanguageDetectionRequest
from src.schemas.language_detection_response import LanguageDetectionResponse


router = APIRouter()

@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(request: LanguageDetectionRequest):
    return LanguageDetectionPipeline().run(request)
