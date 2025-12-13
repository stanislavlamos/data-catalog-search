from typing import Literal
from dotenv import load_dotenv
from openai import OpenAI, Omit
from openai.types.vector_store_create_params import ExpiresAfter

from src.services.nkod_data_processor import NkodDataProcessor
import pandas as pd
from tqdm import tqdm
from src.utils import dir_name_from_uri
import os
import json


load_dotenv()

class OpenaiVectorStoresCreator:
    def __init__(self, catalog_name: str = "nkod"):
        self.nkod_data_processor = NkodDataProcessor(catalog_name)
        self.client = OpenAI()

    def create_vector_stores(self):
        df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)
        vector_store_ids = {}

        for dataset_uri in tqdm(df["dataset_uri"], desc="Creating vector stores"):
            vs_name = dir_name_from_uri(dataset_uri)
            dir_name = dir_name_from_uri(dataset_uri)
            f_id = self.upload_files(dir_name)

            vector_store = self.client.vector_stores.create(
                name=vs_name,
                chunking_strategy=Omit(),
                file_ids=f_id,
                expires_after=ExpiresAfter(
                    anchor="last_active_at",
                    days=365
                )
            )
            vector_store_ids[vs_name] = vector_store.id

        with open(self.nkod_data_processor.vector_stores_json, "w") as f:
            json.dump(vector_store_ids, f, indent=4)

    def upload_files(self, dir_name: str, purpose: Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"] = "assistants") -> list[str]:
        fpath = os.path.join(self.nkod_data_processor.distribution_download_location, dir_name, "distribution_expanded.txt")
        with open(fpath, "rb") as f:
            uploaded_file = self.client.files.create(
                file=f,
                purpose=purpose
            )

        return [uploaded_file.id]
