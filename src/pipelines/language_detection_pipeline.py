from src.schemas.language_detection_request import LanguageDetectionRequest
from src.schemas.language_detection_response import LanguageDetectionResponse
from src.services.language_detector import LanguageDetector
from src.models.model_handler import LLMProviderHandler


class LanguageDetectionPipeline:
    @staticmethod
    def run(language_detector_request: LanguageDetectionRequest) -> LanguageDetectionResponse:
        llm_provider = LLMProviderHandler.get_model(
            provider_name=language_detector_request.llm_provider,
            model_name=language_detector_request.model_name
        )
        language_detector = LanguageDetector()
        response = language_detector.detect(
            text=language_detector_request.text,
            model_name=language_detector_request.model_name,
            llm_provider=llm_provider
        )

        return LanguageDetectionResponse(text=str(response))
