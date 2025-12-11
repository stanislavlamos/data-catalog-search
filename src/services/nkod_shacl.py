from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.base import BaseLLMProvider
from src.services.nkod_data_processor import NkodDataProcessor
import os
from pathlib import Path
from src.prompts import nkod_shacl_user, nkod_shacl_system
from src.utils import dir_name_from_uri


class NkodShacl:

    DATA_DIR = "data"
    NKOD_FILE_FORMAT_PREFIX = "http://publications.europa.eu/resource/authority/file-type/"

    def __init__(self, catalog_name: str = "nkod"):
        self.catalog_name = catalog_name
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
        self.nonrdf_file_formats_schema = ['csv', 'json', 'xml']
        self.rdf_file_formats = ['jsonld', 'ttl', 'trig', 'rdf', 'nq', 'nt']
        self.schema_and_distribution_preference = {
            "ttl": 0,
            "rdf": 1,
            "jsonld": 2,
            "trig": 3,
            "nq": 4, 
            "nt": 5
        }

    def generate_sparql_query(self, user_query: str, matched_lst_dict: list[dict], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, language: str, sq_lite: SqLite, graph_db: GraphDb) -> str:
        titles_str = "\n".join([distribution["title_cs"] for distribution in matched_lst_dict])
        publishers_str = "\n".join([distribution["publisher_cs"] for distribution in matched_lst_dict])

        sparql_query = llm_provider.chat(
            user_prompt=nkod_shacl_user[model_name],
            user_prompt_vars={
                "user_question": user_query,
                "schemas": self.format_schemas_for_prompt(matched_lst_dict, nkod_data_processor),
                "publishers": publishers_str,
                "titles": titles_str
            },
            system_prompt=nkod_shacl_system[model_name]
        )

        return sparql_query.content[0]["text"]

    def format_schemas_for_prompt(self, matched_lst_dict: list[dict], nkod_data_processor: NkodDataProcessor) -> str:
        schemas_str = ""

        for idx, distribution in enumerate(matched_lst_dict):
            dataset_uri = distribution["dataset_uri"]
            dir_name = dir_name_from_uri(dataset_uri)

            with open(os.path.join(nkod_data_processor.distribution_download_location, dir_name, "shacl.ttl"), "r", encoding="utf-8") as f:
                content = f.read()
                schema_format = "Turtle"

            schemas_str += f"""
                Schema {idx + 1} (format: {schema_format}):
                {content}
                \n\n
            """

        return schemas_str
    