from pydantic import BaseModel


class NkodQueryMatcherResponse(BaseModel):
    matched_lst_dict: list[dict]
