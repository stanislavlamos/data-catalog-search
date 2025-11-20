from fastapi import FastAPI
from src.api import match_query_router
from src.api.detect_language_router import router as detect_language_router
from src.api.detect_timeframe_router import router as detect_timeframe_router
from src.api.match_query_router import router as match_query_router
from src.api.get_all_datasets_router import router as get_all_datasets_router
from src.api.nkod_rag_router import router as nkod_rag_router
from src.api.nkod_graph_sparql_router import router as nkod_graph_sparql_router
from src.api.nkod_openai_files_router import router as nkod_openai_files_router
from src.api.nkod_shacl_router import router as nkod_shacl_router


app = FastAPI()
app.include_router(detect_language_router)
app.include_router(detect_timeframe_router)
app.include_router(match_query_router)
app.include_router(get_all_datasets_router)
app.include_router(nkod_rag_router)
app.include_router(nkod_graph_sparql_router)
app.include_router(nkod_openai_files_router)
app.include_router(nkod_shacl_router)
