from pydantic import BaseModel


class LanguageDetectionRequest(BaseModel):
    text: str
    llm_provider: str
    model_name: str = "gpt-4.1-mini"
