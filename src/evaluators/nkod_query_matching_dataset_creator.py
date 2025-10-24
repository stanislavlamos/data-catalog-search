import os.path
from src.prompts import nkod_query_matching_dataset_simple_system, nkod_query_matching_dataset_simple_user
from src.models.base import BaseLLMProvider
from src.utils import get_n_random_list_idxs, save_list_as_jsonl, \
    split_dataset_creation_sql_output
from src.db.sq_lite import SqLite
from src.schemas.schemas import InputLanguage, QueryGeneration
from src.services.nkod_data_processor import NkodDataProcessor
from src.sql_queries import get_titles_and_descs_czech_nkod, get_titles_and_descs_english_nkod


class NkodQueryMatchingDatasetCreator:
    def __init__(self):
        self.random_samples_simple = []
        self.fname_simple_cs = "nkod_query_matching_dataset_simple_cs.jsonl"
        self.fname_simple_en = "nkod_query_matching_dataset_simple_en.jsonl"

    def create_dataset(self, n: int, nkod_data_processor: NkodDataProcessor, sq_lite: SqLite, language: InputLanguage, llm_provider: BaseLLMProvider, model_name: str, seed: int = 15):
        self.random_samples_simple = self._get_samples_simple(n, nkod_data_processor, sq_lite, language, seed)
        simple_queries = self.get_simple_queries(llm_provider, language.value, model_name)
        cur_fname_simple = self.fname_simple_cs if language is InputLanguage.CZECH else self.fname_simple_en

        save_list_as_jsonl(simple_queries, os.path.join(nkod_data_processor.data_path, cur_fname_simple))

    def _get_samples_simple(self, n: int, nkod_data_processor: NkodDataProcessor, sq_lite: SqLite, language: InputLanguage, seed: int = 15) -> list[dict]:
        if language is InputLanguage.CZECH:
            result_descs_and_titles = sq_lite.query_data(get_titles_and_descs_czech_nkod, {"table_name": nkod_data_processor.metadata_sql_table_name})
        else: # language is InputLanguage.ENGLISH
            result_descs_and_titles = sq_lite.query_data(get_titles_and_descs_english_nkod, {"table_name": nkod_data_processor.metadata_sql_table_name})

        split_result = split_dataset_creation_sql_output(result_descs_and_titles, language.value)
        random_idxs = get_n_random_list_idxs(len(split_result), n, seed)
        random_sample_results = [split_result[i] for i in random_idxs]

        return random_sample_results

    def get_simple_queries(self, llm_provider: BaseLLMProvider, language: str, model_name: str = "gpt-5") -> list[dict]:
        simple_queries = []

        for cur_dict in self.random_samples_simple:
            generated_query = llm_provider.chat(
                user_prompt=nkod_query_matching_dataset_simple_user[model_name],
                user_prompt_vars={
                    "dataset_uri": cur_dict["dataset_uri"],
                    "language": language,
                    "title": cur_dict[f"title_{language}"],
                    "description": cur_dict[f"description_{language}"]
                },
                system_prompt=nkod_query_matching_dataset_simple_system[model_name],
                structured_output=QueryGeneration
            )

            simple_queries.append({
                "dataset_uri": cur_dict["dataset_uri"],
                "title": cur_dict[f"title_{language}"],
                "description": cur_dict[f"description_{language}"],
                "query": generated_query.generated_query,
                "language": language,
            })

        return simple_queries
