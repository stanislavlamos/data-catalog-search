from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.base import BaseLLMProvider
from src.prompts import nkod_graph_sparql_user, nkod_graph_sparq_system
from src.schemas.schemas import NkodDistribution
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_dataset_processor import NkodDatasetProcessor
from src.utils import dir_name_from_uri
import json
import os


class NkodGraphSparql:
    def __init__(self):
        self.nkod_dataset_processor = NkodDatasetProcessor()

    def generate_sparql_query(self, user_query: str, matched_lst_dict: list[dict], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, language: str, sq_lite: SqLite, graph_db: GraphDb) -> str:
        titles_str = "\n".join([distribution["title_cs"] for distribution in matched_lst_dict])
        publishers_str = "\n".join([distribution["publisher_cs"] for distribution in matched_lst_dict])
        classes, relationships = self.load_relationships(matched_lst_dict, nkod_data_processor)

        sparql_query = llm_provider.chat(
            user_prompt=nkod_graph_sparql_user[model_name],
            user_prompt_vars={
                "question": user_query,
                "classes": classes,
                "relationships": relationships,
                "publishers": publishers_str,
                "titles": titles_str
            },
            system_prompt=nkod_graph_sparq_system[model_name]
        )

        return sparql_query.content[0]["text"]
    
    def load_relationships(self, matched_lst_dict: list[dict], nkod_data_processor: NkodDataProcessor) -> tuple[str, str]:
        classes = []
        relationships = []

        for distribution in matched_lst_dict:
            dataset_uri = distribution["dataset_uri"]
            dir_name = dir_name_from_uri(dataset_uri)

            with open(os.path.join(nkod_data_processor.distribution_download_location, dir_name, "properties.json"), "r", encoding="utf-8") as f:
                data = json.load(f)
            
            classes.append(data["classes"])
            classes.append(data["relationships"])
        
        return ', '.join(classes), ', '.join(relationships)
