from pydantic import BaseModel


class NkodQueryMatcherResponse(BaseModel):
    matched_titles: list[dict]
    matched_descriptions: list[dict]
    matched_keywords: list[dict]
