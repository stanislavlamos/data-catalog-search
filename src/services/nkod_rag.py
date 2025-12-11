from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.base import BaseLLMProvider
from src.services.nkod_data_processor import NkodDataProcessor
from src.prompts import nkod_rag_user, nkod_rag_system
import pandas as pd
from pathlib import Path
from src.utils import dir_name_from_uri
import os
import json


class NkodRAG:
    def generate_sparql_query(self, user_query: str, matched_lst_dict: list[dict], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, language: str, sq_lite: SqLite, graph_db: GraphDb) -> str:
        titles_str = "\n".join([distribution["title_cs"] for distribution in matched_lst_dict])
        publishers_str = "\n".join([distribution["publisher_cs"] for distribution in matched_lst_dict])

        sparql_query = llm_provider.chat(
            user_prompt=nkod_rag_user[model_name],
            user_prompt_vars={
                "user_question": user_query,
                "schemas": self.format_schemas_for_prompt(matched_lst_dict, nkod_data_processor),
                "publishers": publishers_str,
                "titles": titles_str
            },
            system_prompt=nkod_rag_system[model_name]
        )

        return sparql_query.content[0]["text"]

    def format_schemas_for_prompt(self, matched_lst_dict: list[dict], nkod_data_processor: NkodDataProcessor) -> str:
        schemas_str = ""

        for idx, distribution in enumerate(matched_lst_dict):
            dataset_uri = distribution["dataset_uri"]
            dir_name = dir_name_from_uri(dataset_uri)
            json_schema_path = Path(os.path.join(nkod_data_processor.distribution_download_location, dir_name, "schema.json"))

            if json_schema_path.exists():
                with open(os.path.join(nkod_data_processor.distribution_download_location, dir_name, "schema.json"), "r", encoding="utf-8") as f:
                    content = json.load(f)
                    schema_format = "JSON"
            else:
                with open(os.path.join(nkod_data_processor.distribution_download_location, dir_name, "shacl.ttl"), "r", encoding="utf-8") as f:
                    content = f.read()
                    schema_format = "Turtle"

            schemas_str += f"""
                Schema {idx + 1} (format: {schema_format}):
                {content}
                \n\n
            """

        return schemas_str
