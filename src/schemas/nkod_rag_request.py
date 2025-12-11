from pydantic import BaseModel


class NkodRagRequest(BaseModel):
    query: str
    matched_lst_dict: list[dict]
    provider_name: str = "openai"
    model_name: str
    language: str
