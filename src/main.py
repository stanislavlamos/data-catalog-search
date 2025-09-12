from fastapi import FastAPI
from src.api.update_nkod_data_router import router as update_nkod_data_router


app = FastAPI()
app.include_router(update_nkod_data_router)
