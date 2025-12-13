from pathlib import Path
from typing import Literal
from openai import OpenAI
from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.base import BaseLLMProvider
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_dataset_processor import NkodDatasetProcessor
from dotenv import load_dotenv
import os
from src.prompts import nkod_openai_files_user, nkod_openai_files_system, nkod_openai_files_error_user
from src.utils import dir_name_from_uri, format_publishers_or_titles, load_multiple_jsons_to_list, \
    format_few_shot_examples, get_few_shot_fnames
import json


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

        self.format_to_extension_distribution = {
            "json-ld": "jsonld",
            "json_ld": "jsonld",
            "rdf_n_triples": "nt",
            "rdf_turtle": "ttl",
            "rdf_n_quads": "nq",
            "rdf_trig": "trig",
            "csv": "csv",
            "zip": "zip",
            "rdf_xml": "rdf",
            "json": "json",
            "xml": "xml"
        }

    def generate_sparql_query(self, user_query: str, matched_lst_dict: list[dict], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, language: str, sq_lite: SqLite, graph_db: GraphDb, vs_id: str | None) -> tuple[str, str]:
        titles_str = format_publishers_or_titles([distribution["title_cs"] for distribution in matched_lst_dict])
        publishers_str = format_publishers_or_titles([distribution["publisher_cs"] for distribution in matched_lst_dict])
        files_ids = self.upload_files(matched_lst_dict, nkod_data_processor) if vs_id is None else None

        sparql_query, new_vs_id = llm_provider.chat(
            user_prompt=nkod_openai_files_user[model_name],
            system_prompt=nkod_openai_files_system[model_name],
            user_prompt_vars={
                "user_question": user_query,
                "publishers": publishers_str,
                "titles": titles_str,
                "few_shot_queries": self.get_few_shots(matched_lst_dict, nkod_data_processor)
            },
            file_ids=files_ids,
            purpose="OPENAI_FILES_PIPELINE",
            vector_store_id=vs_id
        )
        
        return sparql_query, new_vs_id

    def generate_sparql_query_error(self, user_query: str, matched_lst_dict: list[dict], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, language: str, sq_lite: SqLite, graph_db: GraphDb, error: str, failing_query: str, vs_id: str | None) -> tuple[str, str]:
        titles_str = format_publishers_or_titles([distribution["title_cs"] for distribution in matched_lst_dict])
        publishers_str = format_publishers_or_titles([distribution["publisher_cs"] for distribution in matched_lst_dict])
        files_ids = self.upload_files(matched_lst_dict, nkod_data_processor) if vs_id is None else None

        sparql_query, new_vs_id = llm_provider.chat(
            user_prompt = nkod_openai_files_error_user[model_name],
            user_prompt_vars={
                "user_question": user_query,
                "publishers": publishers_str,
                "titles": titles_str,
                "few_shot_queries": self.get_few_shots(matched_lst_dict, nkod_data_processor),
                "stack_trace": error,
                "failing_query": failing_query,
            },
            system_prompt = nkod_openai_files_system[model_name],
            purpose="OPENAI_FILES_ERROR_PIPELINE",
            file_ids=files_ids,
            vector_store_id=vs_id
        )

        return sparql_query, new_vs_id

    def upload_file(self, file_path: str, purpose: Literal["assistants", "batch", "fine-tune", "vision", "user_data", "evals"] = "assistants") -> str:
        with open(file_path, "rb") as f:
            uploaded_file = self.client.files.create(
                file=f,
                purpose=purpose
            )

        return uploaded_file.id
    
    def upload_files(self, matched_lst_dict: list[dict], nkod_data_processor: NkodDataProcessor) -> list[str]:
        uploaded_file_ids = []

        for dataset in matched_lst_dict:
            dir_name = dir_name_from_uri(dataset["dataset_uri"])
            file_id = self.upload_file(os.path.join(nkod_data_processor.distribution_download_location, dir_name, "distribution_expanded.txt"))
            uploaded_file_ids.append(file_id)

        return uploaded_file_ids

    def get_few_shots(self, matched_lst_dict: list[dict], nkod_data_processor: NkodDataProcessor) -> str:
        ofns = list(set([distribution["matched_substring"] for distribution in matched_lst_dict]))
        few_shots_lst = load_multiple_jsons_to_list([os.path.join(nkod_data_processor.data_path, fname) for fname in get_few_shot_fnames(ofns)])
        few_shots_str = format_few_shot_examples(few_shots_lst)

        return few_shots_str
    