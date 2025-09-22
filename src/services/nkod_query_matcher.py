from datetime import date
from src.db.chroma_db import ChromaDb
from src.models.base import BaseEmbeddingProvider, BaseLLMProvider
from src.models.schemas import InputLanguage, TimeframeDetection
from src.prompts import timeframe_detection_user, timeframe_detection_system
from src.services.base_query_matcher import BaseQueryMatcher
from src.services.nkod_data_processor import NkodDataProcessor
from src.utils import get_uris_from_chroma_query


class NkodQueryMatcher(BaseQueryMatcher):
    def __init__(self, query: str):
        self.query = query
        self.matching_keywords = []
        self.matching_descriptions = []
        self.matching_titles = []
        self.matching_distributions = []

    def high_k_intersection(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: InputLanguage, embedding_provider: BaseEmbeddingProvider) -> list:
        matching_titles = self.get_matching_titles(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_descriptions = self.get_matching_descriptions(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_keywords = self.get_matching_keywords(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_attributes = [matching_titles, matching_descriptions, matching_keywords]
        intersection = self.get_intersection(matching_attributes)

        return intersection

    def high_k_intersection_llm(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: InputLanguage, embedding_provider: BaseEmbeddingProvider):
        matching_titles = self.get_matching_titles(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_descriptions = self.get_matching_descriptions(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_keywords = self.get_matching_keywords(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_attributes = [matching_titles, matching_keywords, matching_descriptions]
        intersection = self.get_intersection(matching_attributes)

    def high_k_intersection_new_keywords(self, k: int):
        pass

    def get_matching_distributions(self):
        pass

    def get_matching_keywords(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider) -> list[str]:
        collection_name = f"{nkod_data_processor.keywords_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        query_result = get_uris_from_chroma_query(chroma_db.similarity_search([self.query], k)["metadatas"])

        return query_result

    def get_matching_descriptions(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider) -> list[str]:
        collection_name = f"{nkod_data_processor.descriptions_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        query_result = get_uris_from_chroma_query(chroma_db.similarity_search([self.query], k)["metadatas"])

        return query_result

    def get_matching_titles(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider) -> list[str]:
        collection_name = f"{nkod_data_processor.titles_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        query_result = get_uris_from_chroma_query(chroma_db.similarity_search([self.query], k)["metadatas"])

        return query_result

    def derive_k_keywords_from_query(self, k, query: str, language: InputLanguage, llm_provider: BaseLLMProvider, model_name: str) -> list[str]:
        pass

    def get_intersection(self, input_lists: list[list]) -> list:
        return list(set(input_lists[0]).intersection(*map(set, input_lists[1:])))

