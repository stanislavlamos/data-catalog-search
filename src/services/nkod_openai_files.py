from pathlib import Path
from openai import OpenAI
from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.base import BaseLLMProvider
from src.schemas.schemas import NkodDistribution
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_dataset_processor import NkodDatasetProcessor
from dotenv import load_dotenv
import requests
from datetime import datetime
import json
import os
from src.prompts import nkod_openai_files_user, nkod_openai_files_system


load_dotenv()

class NkodOpenAiFiles:

    DATA_DIR = "data"
    NKOD_FILE_FORMAT_PREFIX = "http://publications.europa.eu/resource/authority/file-type/"

    def __init__(self, catalog_name: str = "nkod", include_entities: bool = False):
        self.catalog_name = catalog_name
        self.nkod_dataset_processor = NkodDatasetProcessor()
        self.include_entities = include_entities
        self.client = OpenAI()

        project_dir = Path(__file__).resolve().parent.parent.parent
        self.data_path = os.path.join(project_dir, self.DATA_DIR, self.catalog_name)
        self.tmp_folder_path = os.path.join(self.data_path, "tmp")

    def generate_sparql_query(self, user_query: str, orig_distributions: list[list[NkodDistribution]], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, dataset_uris: list[str], language: str, sq_lite: SqLite, graph_db: GraphDb) -> tuple[str, list[NkodDistribution]]:
        processed_datasets = self.nkod_dataset_processor.process_datasets(orig_distributions)
        titles = self.get_dataset_titles(nkod_data_processor, sq_lite, dataset_uris, language)
        publishers = self.get_dataset_publishers(nkod_data_processor, graph_db, dataset_uris, language)
        titles_str = "\n".join(titles)
        publishers_str = "\n".join(publishers)

        sparql_query = llm_provider.chat(
            user_prompt=nkod_openai_files_user[model_name],
            system_prompt=nkod_openai_files_system[model_name],
            user_prompt_vars={
                "user_question": user_query,
                "publishers": publishers_str,
                "titles": titles_str
            }
        )

        print(processed_datasets)

        return sparql_query.content, processed_datasets

    def upload_file(self, file_path: str, purpose: str = "assistants") -> str:
        with open(file_path, "rb") as f:
            uploaded_file = self.client.files.create(
                file=f,
                purpose=purpose
            )

        return uploaded_file.id
    
    def upload_files(self, datasets: list[NkodDistribution]) -> list[str]:
        uploaded_file_ids = []

        for dataset in datasets:
            input_filename = self.download_dataset(dataset)
            file_id = self.upload_file(os.path.join(self.tmp_folder_path, input_filename))
            uploaded_file_ids.append(file_id)

        return uploaded_file_ids

    def download_dataset(self, distribution: NkodDistribution) -> str:
        input_file_str = requests.get(distribution.downloadURL).text
        input_file_extension = self.get_distribution_format(distribution)

        if input_file_extension is None:
            raise ValueError("Cannot determine distribution file format.")

        now = datetime.now()
        input_filename = f"distribution_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"

        if input_file_extension == "jsonld":
            data = json.loads(input_file_str)

            with open(os.path.join(self.tmp_folder_path, input_filename), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        else:
            with open(os.path.join(self.tmp_folder_path, input_filename), "w", encoding="utf-8") as f:
                f.write(input_file_str)
        
        return input_filename
    
    def download_datasets(self, datasets: list[NkodDistribution]) -> list[str]:
        downloaded_files = []

        for dataset in datasets:
            downloaded_files.append(self.download_dataset(dataset))

        return downloaded_files
    
    def get_distribution_format(self, distribution: NkodDistribution) -> str | None:
        if distribution.format.startswith(self.NKOD_FILE_FORMAT_PREFIX):
            format_key = distribution.format.replace(self.NKOD_FILE_FORMAT_PREFIX, "")
            file_extension = self.format_to_extension_distribution.get(format_key.lower(), None)
            return file_extension

        return None
    
    def get_dataset_publishers(self, nkod_data_processor: NkodDataProcessor, graph_db: GraphDb, dataset_uris: list[str], language: str) -> list[str]:
        publishers = []

        for dataset_uri in dataset_uris:
            publisher = nkod_data_processor.get_dataset_publisher(dataset_uri, graph_db, language)
            publishers.append(publisher)

        return publishers

    def get_dataset_titles(self, nkod_data_processor: NkodDataProcessor, sq_lite: SqLite, dataset_uris: list[str], language: str) -> list[str]:
        titles = []

        for dataset_uri in dataset_uris:
            title = nkod_data_processor.get_dataset_title(dataset_uri, sq_lite, language)
            titles.append(title)

        return titles