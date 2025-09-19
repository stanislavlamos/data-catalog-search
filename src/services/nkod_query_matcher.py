from datetime import date
from src.db.chroma_db import ChromaDb
from src.models.base import BaseEmbeddingProvider, BaseLLMProvider
from src.models.schemas import InputLanguage, TimeframeDetection
from src.prompts import timeframe_detection_user, timeframe_detection_system
from src.services.base_query_matcher import BaseQueryMatcher
from src.services.nkod_data_processor import NkodDataProcessor


class NkodQueryMatcher(BaseQueryMatcher):
    def __init__(self, query: str):
        self.query = query
        self.matching_keywords = []
        self.matching_descriptions = []
        self.matching_titles = []
        self.matching_distributions = []

    def low_k_intersection(self, k: int):
        pass

    def high_k_intersection(self, k: int):
        pass

    def high_k_intersection_llm(self, k: int):
        pass

    def get_matching_distributions(self):
        pass

    def _get_matching_keywords(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: InputLanguage, embedding_provider: BaseEmbeddingProvider):
        collection_name = f"{nkod_data_processor.keywords_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        query_result = chroma_db.similarity_search([self.query], k)

    def _get_matching_descriptions(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: InputLanguage, embedding_provider: BaseEmbeddingProvider):
        collection_name = f"{nkod_data_processor.descriptions_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        query_result = chroma_db.similarity_search([self.query], k)

    def _get_matching_titles(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: InputLanguage, embedding_provider: BaseEmbeddingProvider):
        collection_name = f"{nkod_data_processor.titles_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        query_result = chroma_db.similarity_search([self.query], k)

    def _get_time_frame(self, llm_provider: BaseLLMProvider, model_name: str) -> TimeframeDetection:
        today = date.today().isoformat()
        response = llm_provider.chat(
            user_prompt=timeframe_detection_user[model_name],
            user_prompt_vars={
                "user_query": self.query
            },
            system_prompt=timeframe_detection_system[model_name],
            system_prompt_vars={
                "today": today
            },
            structured_output=TimeframeDetection
        )

        return response