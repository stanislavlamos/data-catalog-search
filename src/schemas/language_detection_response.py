from pydantic import BaseModel


class LanguageDetectionResponse(BaseModel):
    text: str
