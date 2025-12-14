from src.models.model_handler import LLMProviderHandler
from src.schemas.timeframe_detection_request import TimeframeDetectionRequest
from src.schemas.timeframe_detection_response import TimeframeDetectionResponse
from src.services.timeframe_detector import TimeframeDetector


class TimeframeDetectionPipeline:
    @staticmethod
    def run(timeframe_detector_request: TimeframeDetectionRequest) -> TimeframeDetectionResponse:
        llm_provider = LLMProviderHandler.get_model(
            provider_name=timeframe_detector_request.llm_provider,
            model_name=timeframe_detector_request.model_name
        )
        language_detector = TimeframeDetector()
        response = language_detector.detect(
            text=timeframe_detector_request.text,
            model_name=timeframe_detector_request.model_name,
            llm_provider=llm_provider
        )

        return TimeframeDetectionResponse(
            timeframe_specified=response.timeframe_specified,
            start_date=response.start_date,
            end_date=response.end_date
        )
