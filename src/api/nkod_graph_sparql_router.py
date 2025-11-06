from fastapi import APIRouter
from src.pipelines.nkod_graph_sparql_pipeline import NkodGraphSparqlPipeline
from src.schemas.nkod_graph_sparql_request import NkodGraphSparqlRequest
from src.schemas.nkod_graph_sparql_response import NkodGraphSparqlResponse


router = APIRouter()

@router.post("/nkod-graph-sparql", response_model=NkodGraphSparqlResponse)
async def nkod_rag(request: NkodGraphSparqlRequest):
    return NkodGraphSparqlPipeline(request).run()