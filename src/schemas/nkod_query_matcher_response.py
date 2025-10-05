from pydantic import BaseModel


class NkodQueryMatcherResponse(BaseModel):
    text: str
