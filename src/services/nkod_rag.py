from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.base import BaseLLMProvider
from src.schemas.schemas import NkodDistribution
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_schema_processor import NkodSChemaProcessor
from src.prompts import nkod_rag_user, nkod_rag_system


class NkodRAG:
    def __init__(self, include_entities: bool = False):
        self.nkod_schema_processor = NkodSChemaProcessor()
        self.include_entities = include_entities

    def generate_sparql_query(self, user_query: str, orig_distributions: list[list[NkodDistribution]], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, dataset_uris: list[str], language: str, sq_lite: SqLite, graph_db: GraphDb) -> tuple[str, list[NkodDistribution]]:
        processed_schemas, distributions = self.nkod_schema_processor.process_schemas(orig_distributions)
        titles = self.get_dataset_titles(nkod_data_processor, sq_lite, dataset_uris, language)
        publishers = self.get_dataset_publishers(nkod_data_processor, graph_db, dataset_uris, language)
        titles_str = "\n".join(titles)
        publishers_str = "\n".join(publishers)

        if not self.include_entities:
            sparql_query = llm_provider.chat(
                user_prompt=nkod_rag_user[model_name],
                user_prompt_vars={
                    "user_question": user_query,
                    "schemas": self.format_schemas_for_prompt(processed_schemas),
                    "publishers": publishers_str,
                    "titles": titles_str
                },
                system_prompt=nkod_rag_system[model_name]
            )

        else:
            pass

        print(f"Used distributions: {distributions}")

        return sparql_query.content[0]["text"], distributions

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