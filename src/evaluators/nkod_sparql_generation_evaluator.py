import os
from pathlib import Path
import pandas as pd
from src.pipelines.nkod_graph_sparql_pipeline import NkodGraphSparqlPipeline
from src.pipelines.nkod_openai_files_pipeline import NkodOpenAiFilesPipeline
from src.pipelines.nkod_rag_pipeline import NkodRagPipeline
from src.pipelines.nkod_shacl_pipeline import NkodShaclPipeline
from src.schemas.nkod_graph_sparql_request import NkodGraphSparqlRequest
from src.schemas.nkod_openai_files_request import NkodOpenAiFilesRequest
from src.schemas.nkod_rag_request import NkodRagRequest
from src.schemas.nkod_shacl_request import NkodShaclRequest
from src.services.nkod_data_processor import NkodDataProcessor
from src.utils import load_jsonl_to_list


class NkodSparqlGenerationEvaluator:

    DATA_DIR = "data"

    def __init__(self):
        self.catalog_name = "nkod"
        project_dir = Path(__file__).resolve().parent.parent.parent
        self.data_path = os.path.join(project_dir, self.DATA_DIR, self.catalog_name)
        self.nkod_data_processor = NkodDataProcessor(self.catalog_name)
    
    def evaluate_on_ofn_dataset_nkod_shacl(self, ofn_dataset_fname: str, q_idx: int  = None):
        ofn_samples = load_jsonl_to_list(os.path.join(self.data_path, ofn_dataset_fname))
        ofn_samples = ofn_samples if q_idx is None else [ofn_samples[q_idx]]
        df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)

        for idx, ofn_sample in enumerate(ofn_samples):
            idx = idx if q_idx is not None else q_idx
            query = ofn_sample['query']
            print(f"Sample #{idx + 1}/{len(ofn_samples)}")
            print(f"Query: {query}")
            print(f"Desc: {ofn_sample['desc']}")

            dataset_uris = ofn_sample['dataset_uris']
            language = ofn_sample['language']
            matched_lst_dict = [df[df["dataset_uri"] == dataset_uri].to_dict() for dataset_uri in dataset_uris]

            request = NkodShaclRequest(
                query=query,
                matched_lst_dict=matched_lst_dict,
                model_name="gpt-5",
                language=language
            )
            response = NkodShaclPipeline(request).run()

            print(f"SPARQL query from NKOD RAG:\n{response.sparql_query}")
            print(f"SPARQL result: \n{response.query_result}")
            print("-" * 80)
            print("\n")
    
    def evaluate_on_ofn_dataset_nkod_rag(self, ofn_dataset_fname: str, q_idx: int  = None):
        ofn_samples = load_jsonl_to_list(os.path.join(self.data_path, ofn_dataset_fname))
        ofn_samples = ofn_samples if q_idx is None else [ofn_samples[q_idx]]
        df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)

        for idx, ofn_sample in enumerate(ofn_samples):
            idx = idx if q_idx is not None else q_idx
            query = ofn_sample['query']
            print(f"Sample #{idx + 1}/{len(ofn_samples)}")
            print(f"Query: {query}")
            print(f"Desc: {ofn_sample['desc']}")

            dataset_uris = ofn_sample['dataset_uris']
            language = ofn_sample['language']
            matched_lst_dict = [df[df["dataset_uri"] == dataset_uri].to_dict() for dataset_uri in dataset_uris]

            request = NkodRagRequest(
                query=query,
                matched_lst_dict=matched_lst_dict,
                model_name="gpt-5",
                language=language
            )
            response = NkodRagPipeline(request).run()

            print(f"SPARQL query from NKOD RAG:\n{response.sparql_query}")
            print(f"SPARQL result: \n{response.query_result}")
            print("-" * 80)
            print("\n")

    def evaluate_on_ofn_dataset_nkod_graph_sparql(self, ofn_dataset_fname: str, q_idx: int  = None):
        ofn_samples = load_jsonl_to_list(os.path.join(self.data_path, ofn_dataset_fname))
        ofn_samples = ofn_samples if q_idx is None else [ofn_samples[q_idx]]
        df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)

        for idx, ofn_sample in enumerate(ofn_samples):
            idx = idx if q_idx is not None else q_idx
            query = ofn_sample['query']
            print(f"Sample #{idx + 1}/{len(ofn_samples)}")
            print(f"Query: {query}")
            print(f"Desc: {ofn_sample['desc']}")

            dataset_uris = ofn_sample['dataset_uris']
            language = ofn_sample['language']
            matched_lst_dict = [df[df["dataset_uri"] == dataset_uri].to_dict() for dataset_uri in dataset_uris]

            request = NkodGraphSparqlRequest(
                query=query,
                matched_lst_dict=matched_lst_dict,
                model_name="gpt-5",
                language=language
            )
            response = NkodGraphSparqlPipeline(request).run()

            print(f"SPARQL query from NKOD RAG:\n{response.sparql_query}")
            print(f"SPARQL result: \n{response.query_result}")
            print("-" * 80)
            print("\n")
    
    def evaluate_on_ofn_dataset_nkod_openai_files(self, ofn_dataset_fname: str, q_idx: int  = None):
        ofn_samples = load_jsonl_to_list(os.path.join(self.data_path, ofn_dataset_fname))
        ofn_samples = ofn_samples if q_idx is None else [ofn_samples[q_idx]]
        df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)

        for idx, ofn_sample in enumerate(ofn_samples):
            idx = idx if q_idx is not None else q_idx
            query = ofn_sample['query']
            print(f"Sample #{idx + 1}/{len(ofn_samples)}")
            print(f"Query: {query}")
            print(f"Desc: {ofn_sample['desc']}")

            dataset_uris = ofn_sample['dataset_uris']
            language = ofn_sample['language']
            matched_lst_dict = [df[df["dataset_uri"] == dataset_uri].to_dict() for dataset_uri in dataset_uris]

            request = NkodOpenAiFilesRequest(
                query=query,
                matched_lst_dict=matched_lst_dict,
                model_name="gpt-5",
                language=language
            )
            response = NkodOpenAiFilesPipeline(request).run()

            print(f"SPARQL query from NKOD RAG:\n{response.sparql_query}")
            print(f"SPARQL result: \n{response.query_result}")
            print("-" * 80)
            print("\n")
