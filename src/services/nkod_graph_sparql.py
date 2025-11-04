from rdflib.query import ResultRow
from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.base import BaseLLMProvider
from src.prompts import nkod_graph_sparql_user, nkod_graph_sparq_system
from src.schemas.schemas import NkodDistribution
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_dataset_processor import NkodDatasetProcessor
from src.services.nkod_rdf_graph import NkodRdfGraph
from src.sparql_queries import get_classes_nkod_local, get_relationships_nkod_local


class NkodGraphSparql:
    def __init__(self, include_entities: bool = False):
        self.nkod_dataset_processor = NkodDatasetProcessor()
        self.include_entities = include_entities

    def generate_sparql_query(self, user_query: str, distributions: list[list[NkodDistribution]], llm_provider: BaseLLMProvider, model_name: str, nkod_data_processor: NkodDataProcessor, dataset_uris: list[str], language: str, sq_lite: SqLite, graph_db: GraphDb) -> tuple[str, list[NkodDistribution]]:
        processed_datasets = self.nkod_dataset_processor.process_datasets(distributions)
        titles = self.get_dataset_titles(nkod_data_processor, sq_lite, dataset_uris, language)
        publishers = self.get_dataset_publishers(nkod_data_processor, graph_db, dataset_uris, language)
        titles_str = "\n".join(titles)
        publishers_str = "\n".join(publishers)

        if not self.include_entities:
            sparql_query = llm_provider.chat(
                user_prompt=nkod_graph_sparql_user[model_name],
                user_prompt_vars={
                    "question": user_query,
                    "classes": self._generate_graph_classes(processed_datasets),
                    "relationships": self._generate_graph_relationships(processed_datasets),
                    "publishers": publishers_str,
                    "titles": titles_str
                },
                system_prompt=nkod_graph_sparq_system[model_name]
            )
        
        else:
            pass

        print(f"Used distributions: {processed_datasets}")

        return sparql_query.content, processed_datasets

    def _generate_graph_classes(self, processed_datasets: list[NkodDistribution]) -> str:
        graph_classes = []

        for processed_dataset in processed_datasets:
            res_classes = NkodRdfGraph.get_graph(processed_dataset).query(get_classes_nkod_local)
            graph_classes.extend([r for r in res_classes if isinstance(r, ResultRow)])

        ', '.join([self._res_to_str(r, 'cls') for r in graph_classes])

    def _generate_graph_relationships(self, processed_datasets: list[NkodDistribution]) -> str:
        graph_relationships = []

        for processed_dataset in processed_datasets:
            res_rel = NkodRdfGraph.get_graph(processed_dataset).query(get_relationships_nkod_local)
            graph_relationships.extend([r for r in res_rel if isinstance(r, ResultRow)])

        ', '.join([self._res_to_str(r, 'rel') for r in graph_relationships])

    def _get_local_name(self, iri: str) -> str:
        if "#" in iri:
            local_name = iri.split("#")[-1]
        elif "/" in iri:
            local_name = iri.split("/")[-1]
        else:
            raise ValueError(f"Unexpected IRI '{iri}', contains neither '#' nor '/'.")

        return local_name

    def _res_to_str(self, res: ResultRow, var: str) -> str:
        return (
            "<"
            + str(res[var])
            + "> ("
            + self._get_local_name(res[var])
            + ", "
            + str(res["com"])
            + ")"
        )

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
