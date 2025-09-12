from enum import Enum
from pydantic import BaseModel, Field


class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class LlmType(str, Enum):
    GPT_5 = "gpt-5"
    GPT_4_1 = "gpt-4.1"
    GPT_3o = "gpt-3o"


class EmbeddingType(str, Enum):
    EMBEDDING_3_SMALL = "text-embedding-3-small"
    EMBEDDING_3_LARGE = "text-embedding-3-large"


class InputLanguage(str, Enum):
    CZECH = "czech"
    ENGLISH = "english"
    OTHER = "other"


class LanguageDetection(BaseModel):
    language: InputLanguage = Field(..., description="Detected language of the input text")

    def __str__(self):
        return self.language.value


class TimeframeDetection(BaseModel):
    timeframe_specified: bool = Field(..., description="true if the user specified a timeframe, otherwise false.")
    start_date: str | None = Field(..., description="Start date in YYYY-MM-DD format or None if not specified.")
    end_date: str | None = Field(..., description="End date in YYYY-MM-DD format or None if not specified.")

    def __str__(self):
        if self.timeframe_specified:
            return f"{self.start_date}->{self.end_date}"
        return "Timeframe not specified"