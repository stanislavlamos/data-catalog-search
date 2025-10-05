from pydantic import BaseModel


class NkodQueryMatcherRequest(BaseModel):
    query: str
    llm_provider: str
    model_name: str
    language: str
    embedding_provider: str
