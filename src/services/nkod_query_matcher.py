import os
from pathlib import Path

from src.db.chroma_db import ChromaDb
from src.models.base import BaseEmbeddingProvider, BaseLLMProvider
from src.schemas.schemas import InputLanguage, DatasetSelectionOutput
from src.prompts import nkod_query_matching_llm_judge_user, \
    nkod_query_matching_llm_judge_system
from src.services.base_query_matcher import BaseQueryMatcher
from src.services.nkod_data_processor import NkodDataProcessor
from src.utils import get_uris_from_chroma_query, merge_chromadb_docs_with_metadatas, \
    get_docs_and_scores_from_chroma_query, get_intersection


class NkodQueryMatcher(BaseQueryMatcher):
    def __init__(self, query: str):
        super().__init__(query)
        self.catalog_name = "nkod"
        project_dir = Path(__file__).resolve().parent.parent.parent
        self.data_path = os.path.join(project_dir, self.DATA_DIR, self.catalog_name)

        self.matching_keywords = []
        self.matching_descriptions = []
        self.matching_titles = []
        self.matching_distributions = []

    def high_k_intersection(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: InputLanguage, embedding_provider: BaseEmbeddingProvider) -> list:
        matching_titles = self.get_matching_titles(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_descriptions = self.get_matching_descriptions(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_keywords = self.get_matching_keywords(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_attributes = [matching_titles, matching_descriptions, matching_keywords]
        intersection = get_intersection(matching_attributes)

        return intersection

    def high_k_intersection_llm(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: InputLanguage, embedding_provider: BaseEmbeddingProvider, llm_provider: BaseLLMProvider) -> tuple[list[str], DatasetSelectionOutput]:
        matching_titles, merged_docs_with_metadatas = self.get_matching_titles_llm(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_descriptions = self.get_matching_descriptions(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_keywords = self.get_matching_keywords(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_attributes = [matching_titles, matching_keywords, matching_descriptions]
        intersection = get_intersection(matching_attributes)
        datasets = "\n".join([f"{i + 1}. Title: {d['title']}\n   URI: {d['dataset_uri']}" for i, d in
                              enumerate(merged_docs_with_metadatas)])

        llm_res = llm_provider.chat(
            user_prompt=nkod_query_matching_llm_judge_user["gpt-5"],
            user_prompt_vars={
                "user_query": self.query,
                "datasets": datasets
            },
            system_prompt=nkod_query_matching_llm_judge_system["gpt-5"],
            structured_output=DatasetSelectionOutput
        )

        return intersection, llm_res

    def get_matching_keywords(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider, with_scores: bool = False) -> list[str] | tuple[list[str], list[tuple[float, str]]]:
        collection_name = f"{nkod_data_processor.keywords_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        similarity_search = chroma_db.similarity_search([self.query], k)
        query_result = get_uris_from_chroma_query(similarity_search["metadatas"])
        query_result_with_scores = get_docs_and_scores_from_chroma_query(similarity_search["documents"], similarity_search["distances"], "dataset_uri")

        if with_scores:
            return query_result, query_result_with_scores

        return query_result

    def get_matching_descriptions(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider, with_scores: bool = False) -> list[str] | tuple[list[str], list[tuple[float, str]]]:
        collection_name = f"{nkod_data_processor.descriptions_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        similarity_search = chroma_db.similarity_search([self.query], k)
        query_result = get_uris_from_chroma_query(similarity_search["metadatas"])
        query_result_with_scores = get_docs_and_scores_from_chroma_query(similarity_search["documents"], similarity_search["distances"], "dataset_uri")

        if with_scores:
            return query_result, query_result_with_scores

        return query_result

    def get_matching_titles(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider, with_scores: bool = False) -> list[str] | tuple[list[str], list[tuple[float, str]]]:
        collection_name = f"{nkod_data_processor.titles_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        similarity_search = chroma_db.similarity_search([self.query], k)
        query_result = get_uris_from_chroma_query(similarity_search["metadatas"])
        query_result_with_scores = get_docs_and_scores_from_chroma_query(similarity_search["documents"], similarity_search["distances"], "dataset_uri")

        if with_scores:
            return query_result,query_result_with_scores

        return query_result

    def get_matching_theme_labels(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider, with_scores: bool = False) -> list[str] | tuple[list[str], list[tuple[float, str]]]:
        collection_name = f"{nkod_data_processor.themes_labels_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        similarity_search = chroma_db.similarity_search([self.query], k)
        query_result = get_uris_from_chroma_query(similarity_search["metadatas"], "theme_name")
        query_result_with_scores = get_docs_and_scores_from_chroma_query(similarity_search["documents"], similarity_search["distances"], "theme_name")

        if with_scores:
            return query_result,query_result_with_scores

        return query_result

    def get_matching_theme_definitions(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider, with_scores: bool = False) -> list[str] | tuple[list[str], list[tuple[float, str]]]:
        collection_name = f"{nkod_data_processor.themes_definitions_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        similarity_search = chroma_db.similarity_search([self.query], k)
        query_result = get_uris_from_chroma_query(similarity_search["metadatas"], "theme_name")
        query_result_with_scores = get_docs_and_scores_from_chroma_query(similarity_search["documents"], similarity_search["distances"], "theme_name")

        if with_scores:
            return query_result,query_result_with_scores

        return query_result

    def get_matching_titles_llm(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider, with_scores: bool = False) -> tuple[list[str], list[dict]]:
        collection_name = f"{nkod_data_processor.titles_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        similarity_search_res = chroma_db.similarity_search([self.query], k)
        merged_docs_with_metadatas = merge_chromadb_docs_with_metadatas(similarity_search_res)
        query_result = get_uris_from_chroma_query(similarity_search_res["metadatas"])

        return query_result, merged_docs_with_metadatas
