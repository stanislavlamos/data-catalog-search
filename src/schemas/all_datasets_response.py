from pydantic import BaseModel


class AllDatasetsResponse(BaseModel):
    all_datasets: list[dict]
