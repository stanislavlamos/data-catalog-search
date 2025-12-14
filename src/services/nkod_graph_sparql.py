from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.base import BaseLLMProvider
from src.prompts import nkod_graph_sparql_user, nkod_graph_sparq_system, nkod_graph_sparql_error_user
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_dataset_processor import NkodDatasetProcessor
from src.utils import dir_name_from_uri, format_publishers_or_titles, load_multiple_jsons_to_list, \
    format_few_shot_examples, get_few_shot_fnames
import json
import os


class NkodGraphSparql:
    def __init__(self):
        self.nkod_dataset_processor = NkodDatasetProcessor()

    def generate_sparql_query(self, user_query: str, matched_lst_dict: list[dict], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, language: str, sq_lite: SqLite, graph_db: GraphDb) -> str:
        titles_str = format_publishers_or_titles([distribution["title_cs"] for distribution in matched_lst_dict])
        publishers_str = format_publishers_or_titles([distribution["publisher_cs"] for distribution in matched_lst_dict])
        classes, relationships = self.load_relationships(matched_lst_dict, nkod_data_processor)

        sparql_query = llm_provider.chat(
            user_prompt=nkod_graph_sparql_user[model_name],
            user_prompt_vars={
                "user_question": user_query,
                "classes": classes,
                "relationships": relationships,
                "publishers": publishers_str,
                "titles": titles_str,
                "few_shot_queries": self.get_few_shots(matched_lst_dict, nkod_data_processor)
            },
            system_prompt=nkod_graph_sparq_system[model_name],
            purpose="GRAPH_SPARQL_PIPELINE"
        )

        return sparql_query.content[0]["text"]

    def generate_sparql_query_error(self, user_query: str, matched_lst_dict: list[dict], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, language: str, sq_lite: SqLite, graph_db: GraphDb, error: str, failing_query: str) -> str:
        titles_str = format_publishers_or_titles([distribution["title_cs"] for distribution in matched_lst_dict])
        publishers_str = format_publishers_or_titles([distribution["publisher_cs"] for distribution in matched_lst_dict])
        classes, relationships = self.load_relationships(matched_lst_dict, nkod_data_processor)

        sparql_query = llm_provider.chat(
            user_prompt = nkod_graph_sparql_error_user[model_name],
            user_prompt_vars = {
                "user_question": user_query,
                "classes": classes,
                "relationships": relationships,
                "publishers": publishers_str,
                "titles": titles_str,
                "stack_trace": error,
                "failing_query": failing_query,
                "few_shot_queries": self.get_few_shots(matched_lst_dict, nkod_data_processor)
            },
            system_prompt = nkod_graph_sparq_system[model_name],
            purpose="GRAPH_SPARQL_ERROR_PIPELINE"
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

    def get_few_shots(self, matched_lst_dict: list[dict], nkod_data_processor: NkodDataProcessor) -> str:
        ofns = list(set([distribution["matched_substring"] for distribution in matched_lst_dict]))
        few_shots_lst = load_multiple_jsons_to_list([os.path.join(nkod_data_processor.data_path, fname) for fname in get_few_shot_fnames(ofns)])
        few_shots_str = format_few_shot_examples(few_shots_lst)

        return few_shots_str
