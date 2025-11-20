from pydantic import BaseModel


class NkodShaclRequest(BaseModel):
    query: str
    dataset_uris: list[str]
    provider_name: str = "openai"
    model_name: str
    language: str
