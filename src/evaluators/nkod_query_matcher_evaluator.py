from pathlib import Path
import os
from src.pipelines.nkod_query_matcher_intersection_pipeline import NkodQueryMatcherIntersectionPipeline
from src.pipelines.nkod_query_matcher_pipeline import NkodQueryMatcherPipeline
from src.schemas.nkod_query_matcher_request import NkodQueryMatcherRequest
from src.services.nkod_data_processor import NkodDataProcessor
from src.utils import load_jsonl_to_list, match_uris
import time


class NkodQueryMatcherEvaluator:
    
    DATA_DIR = "data"

    def __init__(self):
        self.catalog_name = "nkod"
        project_dir = Path(__file__).resolve().parent.parent.parent
        self.data_path = os.path.join(project_dir, self.DATA_DIR, self.catalog_name)
        self.nkod_data_processor = NkodDataProcessor(self.catalog_name)
    
    def evaluate_intersection_on_ofn(self, ofn_dataset_fname: str, q_idx: int  = None):
        ofn_samples = load_jsonl_to_list(os.path.join(self.data_path, ofn_dataset_fname))
        ofn_samples = ofn_samples if q_idx is None else [ofn_samples[q_idx]]

        for idx, ofn_sample in enumerate(ofn_samples):
            idx = idx if q_idx is None else q_idx
            query = ofn_sample['query']
            print(f"Sample #{idx + 1}/{len(ofn_samples)}")
            print(f"Query: {query}")
            print(f"Desc: {ofn_sample['desc']}")

            dataset_uris = ofn_sample['dataset_uris']
            request = NkodQueryMatcherRequest(
                query=query,
                llm_provider="openai",
                model_name="gpt-5",
                language="cs"    
            )
            start = time.time()
            response = NkodQueryMatcherIntersectionPipeline().run(request, True)
            end = time.time()
            print(f"Elapsed time: {end - start:.4f} seconds")
            matches = match_uris(dataset_uris, response.matched_lst_dict)
            print(matches)
            print("-"*80)

    def evaluate_intersection_on_ofn_no_keywords(self, ofn_dataset_fname: str, q_idx: int  = None):
        ofn_samples = load_jsonl_to_list(os.path.join(self.data_path, ofn_dataset_fname))
        ofn_samples = ofn_samples if q_idx is None else [ofn_samples[q_idx]]

        for idx, ofn_sample in enumerate(ofn_samples):
            idx = idx if q_idx is None else q_idx
            query = ofn_sample['query']
            print(f"Sample #{idx + 1}/{len(ofn_samples)}")
            print(f"Query: {query}")
            print(f"Desc: {ofn_sample['desc']}")

            dataset_uris = ofn_sample['dataset_uris']
            request = NkodQueryMatcherRequest(
                query=query,
                llm_provider="openai",
                model_name="gpt-5",
                language="cs"    
            )
            start = time.time()
            response = NkodQueryMatcherIntersectionPipeline().run(request, False)
            end = time.time()
            print(f"Elapsed time: {end - start:.4f} seconds")
            matches = match_uris(dataset_uris, response.matched_lst_dict)
            print(matches)
            print("-"*80)

    def evaluate_intersection_on_ofn_reranking(self, ofn_dataset_fname: str, q_idx: int  = None):
        ofn_samples = load_jsonl_to_list(os.path.join(self.data_path, ofn_dataset_fname))
        ofn_samples = ofn_samples if q_idx is None else [ofn_samples[q_idx]]

        for idx, ofn_sample in enumerate(ofn_samples):
            idx = idx if q_idx is None else q_idx
            query = ofn_sample['query']
            print(f"Sample #{idx + 1}/{len(ofn_samples)}")
            print(f"Query: {query}")
            print(f"Desc: {ofn_sample['desc']}")

            dataset_uris = ofn_sample['dataset_uris']
            request = NkodQueryMatcherRequest(
                query=query,
                llm_provider="openai",
                model_name="gpt-5",
                language="cs"    
            )
            start = time.time()
            response = NkodQueryMatcherPipeline().run(request)
            end = time.time()
            print(f"Elapsed time: {end - start:.4f} seconds")
            matches = match_uris(dataset_uris, response.matched_lst_dict)
            print(matches)
            print("-"*80)
