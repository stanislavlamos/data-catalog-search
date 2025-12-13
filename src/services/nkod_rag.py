from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.base import BaseLLMProvider
from src.services.nkod_data_processor import NkodDataProcessor
from src.prompts import nkod_rag_user, nkod_rag_system, nkod_rag_error_user
import pandas as pd
from pathlib import Path
from src.utils import dir_name_from_uri, format_publishers_or_titles, format_schemas_for_prompt, \
    load_multiple_jsons_to_list, format_few_shot_examples, get_few_shot_fnames
import os
import json


class NkodRAG:
    def generate_sparql_query(self, user_query: str, matched_lst_dict: list[dict], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, language: str, sq_lite: SqLite, graph_db: GraphDb) -> str:
        titles_str = format_publishers_or_titles([distribution["title_cs"] for distribution in matched_lst_dict])
        publishers_str = format_publishers_or_titles([distribution["publisher_cs"] for distribution in matched_lst_dict])

        sparql_query = llm_provider.chat(
            user_prompt=nkod_rag_user[model_name],
            user_prompt_vars={
                "user_question": user_query,
                "schemas": self.format_schemas_for_prompt(matched_lst_dict, nkod_data_processor),
                "publishers": publishers_str,
                "titles": titles_str,
                "few_shot_queries": self.get_few_shots(matched_lst_dict, nkod_data_processor)
            },
            system_prompt=nkod_rag_system[model_name],
            purpose="RAG_PIPELINE"
        )

        return sparql_query.content[0]["text"]

    def generate_sparql_query_error(self, user_query: str, matched_lst_dict: list[dict], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, language: str, sq_lite: SqLite, graph_db: GraphDb, error: str, failing_query: str) -> str:
        titles_str = format_publishers_or_titles([distribution["title_cs"] for distribution in matched_lst_dict])
        publishers_str = format_publishers_or_titles([distribution["publisher_cs"] for distribution in matched_lst_dict])

        sparql_query = llm_provider.chat(
            user_prompt = nkod_rag_error_user[model_name],
            user_prompt_vars = {
                "user_question": user_query,
                "schemas": self.format_schemas_for_prompt(matched_lst_dict, nkod_data_processor),
                "publishers": publishers_str,
                "titles": titles_str,
                "stack_trace": error,
                "failing_query": failing_query,
                "few_shot_queries": self.get_few_shots(matched_lst_dict, nkod_data_processor)
            },
            system_prompt = nkod_rag_system[model_name],
            purpose="RAG_ERROR_PIPELINE"
        )

        return sparql_query.content[0]["text"]

    def format_schemas_for_prompt(self, matched_lst_dict: list[dict], nkod_data_processor: NkodDataProcessor) -> str:
        schemas = []
        formats = []

        for idx, distribution in enumerate(matched_lst_dict):
            dataset_uri = distribution["dataset_uri"]
            dir_name = dir_name_from_uri(dataset_uri)
            json_schema_path = Path(os.path.join(nkod_data_processor.distribution_download_location, dir_name, "schema.json"))

            if json_schema_path.exists():
                with open(os.path.join(nkod_data_processor.distribution_download_location, dir_name, "schema.json"), "r", encoding="utf-8") as f:
                    content = json.dumps(json.load(f))
                    schema_format = "JSON"
                    schemas.append(content)
                    formats.append(schema_format)

            else:
                with open(os.path.join(nkod_data_processor.distribution_download_location, dir_name, "shacl.ttl"), "r", encoding="utf-8") as f:
                    content = f.read()
                    schema_format = "Turtle"
                    schemas.append(content)
                    formats.append(schema_format)

        return format_schemas_for_prompt(schemas, formats)

    def get_few_shots(self, matched_lst_dict: list[dict], nkod_data_processor: NkodDataProcessor) -> str:
        ofns = list(set([distribution["matched_substring"] for distribution in matched_lst_dict]))
        few_shots_lst = load_multiple_jsons_to_list([os.path.join(nkod_data_processor.data_path, fname) for fname in get_few_shot_fnames(ofns)])
        few_shots_str = format_few_shot_examples(few_shots_lst)

        return few_shots_str
