from fastapi import FastAPI

from src.api import match_query_router
from src.api.detect_language_router import router as detect_language_router
from src.api.detect_timeframe_router import router as detect_timeframe_router
from src.api.match_query_router import router as match_query_router


app = FastAPI()
app.include_router(detect_language_router)
app.include_router(detect_timeframe_router)
app.include_router(match_query_router)
