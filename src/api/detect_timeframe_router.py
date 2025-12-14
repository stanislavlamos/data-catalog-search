from fastapi import APIRouter
from src.pipelines.timeframe_detection_pipeline import TimeframeDetectionPipeline
from src.schemas.timeframe_detection_request import TimeframeDetectionRequest
from src.schemas.timeframe_detection_response import TimeframeDetectionResponse


router = APIRouter()

@router.post("/detect-timeframe", response_model=TimeframeDetectionResponse)
async def detect_timeframe(request: TimeframeDetectionRequest):
    return TimeframeDetectionPipeline.run(request)
