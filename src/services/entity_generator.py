def generate_entities(self, user_query: str, orig_distributions: list[list[NkodDistribution]], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, dataset_uris: list[str], language: str, sq_lite: SqLite, graph_db: GraphDb) -> tuple[str, list[NkodDistribution]]:
        pass

def format_entities_for_prompt(self, entities: list[list[tuple[str, str]]]) -> str:
        pass