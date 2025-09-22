from datetime import date
from src.models.base import BaseLLMProvider
from src.models.schemas import TimeframeDetection
from src.prompts import timeframe_detection_user, timeframe_detection_system


class TimeframeDetector:
    def detect(self, text: str, llm_provider: BaseLLMProvider, model_name: str) -> TimeframeDetection:
        today = date.today().isoformat()

        response = llm_provider.chat(
            user_prompt=timeframe_detection_user[model_name],
            user_prompt_vars={
                "user_query": text
            },
            system_prompt=timeframe_detection_system[model_name],
            system_prompt_vars={
                "today": today
            },
            structured_output=TimeframeDetection
        )

        return response
