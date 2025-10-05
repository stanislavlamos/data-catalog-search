from pydantic import BaseModel


class TimeframeDetectionRequest(BaseModel):
    text: str
    llm_provider: str
    model_name: str
