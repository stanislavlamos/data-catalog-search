from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.base import BaseLLMProvider
from src.schemas.schemas import NkodDistribution
from src.services.nkod_data_processor import NkodDataProcessor
import requests
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from src.prompts import nkod_shacl_user, nkod_shacl_system


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

    def generate_sparql_query(self, user_query: str, orig_distributions: list[list[NkodDistribution]], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, dataset_uris: list[str], language: str, sq_lite: SqLite, graph_db: GraphDb) -> tuple[str, list[NkodDistribution]]:
        processed_schemas, distributions = self.process_schemas(orig_distributions)
        titles = self.get_dataset_titles(nkod_data_processor, sq_lite, dataset_uris, language)
        publishers = self.get_dataset_publishers(nkod_data_processor, graph_db, dataset_uris, language)
        titles_str = "\n".join(titles)
        publishers_str = "\n".join(publishers)

        if not self.include_entities:
            sparql_query = llm_provider.chat(
                user_prompt=nkod_shacl_user[model_name],
                user_prompt_vars={
                    "user_question": user_query,
                    "schemas": self.format_schemas_for_prompt(processed_schemas),
                    "publishers": publishers_str,
                    "titles": titles_str
                },
                system_prompt=nkod_shacl_system[model_name]
            )

        else:
            pass

        print(f"Used distributions: {distributions}")

        return sparql_query.content, distributions

    def format_schemas_for_prompt(self, schemas: list[list[tuple[str, str]]]) -> str:
        schemas_str = ""

        for idx, schema in enumerate(schemas):
            for schema_format, content in schema:
                schemas_str += f"""
                    Schema {idx + 1} (format: {schema_format}):
                    {content}
                    \n
                """

        return schemas_str

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
    
    def process_schemas(self, lst_of_list_of_distributions: list[list[NkodDistribution]]) -> tuple[list[list[tuple[str, str]]], list[NkodDistribution]]:
        processed_schemas_all = []
        selected_distributions = []

        for list_of_distributions in lst_of_list_of_distributions:
            only_files_distributions = self.filter_only_files(list_of_distributions)
            our_distribution = self.select_best_distribution(only_files_distributions)
            selected_distributions.append(our_distribution)
            schema_path = self.generate_shacl(our_distribution)
            processed_schemas_all.append([("ttl", open(schema_path, "r", encoding="utf-8").read())])
                
        return processed_schemas_all, selected_distributions

    def select_best_distribution(self, distributions: list[NkodDistribution]) -> NkodDistribution:
        def score(distribution: NkodDistribution) -> int:
            sort_score = self.schema_and_distribution_preference.get(self.format_to_extension_distribution.get(distribution.format.replace(self.NKOD_FILE_FORMAT_PREFIX, "").lower(), "Unknown format"), 1000)

            if distribution.conformsTo is None:
                sort_score += 10

            return sort_score

        return sorted(distributions, key=score)[0]

    def generate_shacl(self, distribution: NkodDistribution) -> str:
        input_file_str = requests.get(distribution.downloadURL).text
        input_file_extension = self.get_distribution_format(distribution)

        if input_file_extension is None:
            raise ValueError("Cannot determine distribution file format for SHACL generation.")

        now = datetime.now()
        input_filename = f"input_{now.strftime('%Y-%m-%d_%H-%M-%S')}.{input_file_extension}"
        output_filename = f"output_{now.strftime('%Y-%m-%d_%H-%M-%S')}_shacl.ttl"

        if input_file_extension == "jsonld":
            data = json.loads(input_file_str)

            with open(os.path.join(self.tmp_folder_path, input_filename), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        else:
            with open(os.path.join(self.tmp_folder_path, input_filename), "w", encoding="utf-8") as f:
                f.write(input_file_str)
                
        _ = subprocess.run(
            ["shaclgen", os.path.join(self.tmp_folder_path, input_filename), "--output", os.path.join(self.tmp_folder_path, output_filename)],
            check=True,
            capture_output=True,
            text=True
        )

        return os.path.join(self.tmp_folder_path, output_filename)
    
    def filter_only_files(self, distributions: list[NkodDistribution]) -> list[NkodDistribution]:
        filtered_distributions = []

        for distribution in distributions:
            if distribution.format is None or distribution.downloadURL is None:
                continue

            elif not self.is_distribution_file(distribution):
                continue

            filtered_distributions.append(distribution)

        return filtered_distributions
    