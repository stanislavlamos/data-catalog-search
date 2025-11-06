import os
from pathlib import Path
from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.base import BaseLLMProvider
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_graph_sparql import NkodGraphSparql
from src.services.nkod_openai_files import NkodOpenAiFiles
from src.services.nkod_rag import NkodRAG
from src.services.nkod_rdf_graph import NkodRdfGraph
from src.utils import load_jsonl_to_list, delete_sparql_backticks


class NkodSparqlGenerationEvaluator:

    DATA_DIR = "data"

    def __init__(self):
        self.catalog_name = "nkod"
        project_dir = Path(__file__).resolve().parent.parent.parent
        self.data_path = os.path.join(project_dir, self.DATA_DIR, self.catalog_name)

    def evaluate_on_ofn_dataset_nkod_rag(self, ofn_dataset_fname: str, nkod_rag: NkodRAG, nkod_data_processor: NkodDataProcessor, llm_provider: BaseLLMProvider, model_name: str,  graph_db: GraphDb, sq_lite: SqLite, language: str = "cs"):
        ofn_samples = load_jsonl_to_list(os.path.join(self.data_path, ofn_dataset_fname))

        for idx, ofn_sample in enumerate(ofn_samples[:6]):
            query = ofn_sample['query']
            print(f"Sample #{idx + 1}/{len(ofn_samples)}")
            print(f"Query: {query}")
            print(f"Desc: {ofn_sample['desc']}")

            dataset_uris = ofn_sample['dataset_uris']
            distributions = [nkod_data_processor.get_dataset_distributions(dataset_uri, graph_db) for dataset_uri in dataset_uris]

            sparql_query, distributions = nkod_rag.generate_sparql_query(query, distributions, llm_provider, model_name, nkod_data_processor, dataset_uris, language, sq_lite, graph_db)
            print(f"SPARQL query from NKOD RAG:\n{delete_sparql_backticks(sparql_query)}")

            nkod_graph = NkodRdfGraph(distributions)
            query_result = nkod_graph.query_graph(delete_sparql_backticks(sparql_query))
            print(f"SPARQL result: \n{query_result}")

            print("-" * 80)
            print("\n")

    def evaluate_on_ofn_dataset_nkod_graph_sparql(self, ofn_dataset_fname: str, nkod_graph_sparql: NkodGraphSparql, nkod_data_processor: NkodDataProcessor, llm_provider: BaseLLMProvider, model_name: str,  graph_db: GraphDb, sq_lite: SqLite, language: str = "cs"):
        ofn_samples = load_jsonl_to_list(os.path.join(self.data_path, ofn_dataset_fname))

        for idx, ofn_sample in enumerate([ofn_samples[10]]):
            query = ofn_sample['query']
            print(f"Sample #{idx + 1}/{len(ofn_samples)}")
            print(f"Query: {query}")
            print(f"Desc: {ofn_sample['desc']}")

            dataset_uris = ofn_sample['dataset_uris']
            distributions = [nkod_data_processor.get_dataset_distributions(dataset_uri, graph_db) for dataset_uri in dataset_uris]

            sparql_query, distributions = nkod_graph_sparql.generate_sparql_query(query, distributions, llm_provider, model_name, nkod_data_processor, dataset_uris, language, sq_lite, graph_db)
            print(f"SPARQL query from NKOD Graph SPARQL:\n{delete_sparql_backticks(sparql_query)}")

            nkod_graph = NkodRdfGraph(distributions)
            query_result = nkod_graph.query_graph(delete_sparql_backticks(sparql_query))
            print(f"SPARQL result: \n{query_result}")

            print("-" * 80)
            print("\n")
    
    def evaluate_on_ofn_dataset_nkod_openai_files(self, ofn_dataset_fname: str, nkod_openai_files: NkodOpenAiFiles, nkod_data_processor: NkodDataProcessor, llm_provider: BaseLLMProvider, model_name: str,  graph_db: GraphDb, sq_lite: SqLite, language: str = "cs"):
        ofn_samples = load_jsonl_to_list(os.path.join(self.data_path, ofn_dataset_fname))

        for idx, ofn_sample in enumerate([ofn_samples[4]]):
            query = ofn_sample['query']
            print(f"Sample #{idx + 1}/{len(ofn_samples)}")
            print(f"Query: {query}")
            print(f"Desc: {ofn_sample['desc']}")

            dataset_uris = ofn_sample['dataset_uris']
            distributions = [nkod_data_processor.get_dataset_distributions(dataset_uri, graph_db) for dataset_uri in dataset_uris]

            sparql_query, distributions = nkod_openai_files.generate_sparql_query(query, distributions, llm_provider, model_name, nkod_data_processor, dataset_uris, language, sq_lite, graph_db)
            print(f"SPARQL query from NKOD OpenAi Files:\n{delete_sparql_backticks(sparql_query)}")

            nkod_graph = NkodRdfGraph(distributions)
            query_result = nkod_graph.query_graph(delete_sparql_backticks(sparql_query))
            print(f"SPARQL result: \n{query_result}")

            print("-" * 80)
            print("\n")

