from fastapi import APIRouter
from src.pipelines.all_datasets_pipeline import AllDatasetsPipeline
from src.schemas.all_datasets_response import AllDatasetsResponse


router = APIRouter()

@router.get("/get-all-datasets", response_model=AllDatasetsResponse)
async def get_all_datasets():
    return AllDatasetsPipeline().run()
