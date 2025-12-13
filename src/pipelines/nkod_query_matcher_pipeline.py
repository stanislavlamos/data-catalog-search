from src.db.chroma_db import ChromaDb
from src.models.model_handler import LLMProviderHandler, EmbeddingProviderHandler
from src.schemas.nkod_query_matcher_request import NkodQueryMatcherRequest
from src.schemas.nkod_query_matcher_response import NkodQueryMatcherResponse
from src.services.entity_generator import EntityGenerator
from src.services.nkod_data_processor import NkodDataProcessor
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.services.nkod_query_matcher import NkodQueryMatcher
from src.services.nkod_query_matcher_reranker import NkodQueryMatcherReranker
import pandas as pd


class NkodQueryMatcherPipeline:

    BATCH_SIZE = 60

    def __init__(self):
        self. nkod_data_processor = None
        self.chroma_db = None
        self.llm_provider = None
        self.embedding_provider = None
        self.query = None
        self.language = None
        self.nkod_query_matcher = None
        self.k = 30
        self.nkod_query_reranker = None

    def run(self, request: NkodQueryMatcherRequest) -> NkodQueryMatcherResponse:
        self.nkod_data_processor = NkodDataProcessor("nkod")
        self.chroma_db = ChromaDb(self.nkod_data_processor.vectordb_path)
        self.llm_provider = LLMProviderHandler().get_model(provider_name=request.llm_provider, model_name=request.model_name)
        self.embedding_provider = EmbeddingProviderHandler().get_model(provider_name=request.embedding_provider)
        self.language = request.language
        self.query = request.query
        self.nkod_query_matcher = NkodQueryMatcher(self.query)
        self.nkod_query_reranker = NkodQueryMatcherReranker()
        self.entity_generator = EntityGenerator()

        df = self._run_query_matching_parallel()
        reranked_lst_dict = self._run_reranking_ofn_topk(df) #self._run_reranking_ofn(df)
       
        return NkodQueryMatcherResponse(
            matched_lst_dict=reranked_lst_dict
        )

    def _run_query_matching_parallel(self) -> pd.DataFrame:
        tasks = [
            ("matching_titles", self.nkod_query_matcher.get_matching_titles, (self.k, self.chroma_db, self.nkod_data_processor, self.language, self.embedding_provider, True)),
            ("matching_descs", self.nkod_query_matcher.get_matching_descriptions, (self.k, self.chroma_db, self.nkod_data_processor, self.language, self.embedding_provider, True)),
            ("matching_keywords", self.nkod_query_matcher.get_matching_keywords, (self.k, self.chroma_db, self.nkod_data_processor, self.language, self.embedding_provider, True)),
            ("entity_titles", self.nkod_query_matcher.get_matching_entitities_titles, (self.k, self.chroma_db, self.nkod_data_processor, self.language, self.embedding_provider, self.entity_generator, True)),
            ("entity_keywords", self.nkod_query_matcher.get_matching_entitities_keywords, (self.k, self.chroma_db, self.nkod_data_processor, self.language, self.embedding_provider, self.entity_generator, True)),
            ("entity_descriptions", self.nkod_query_matcher.get_matching_entitities_descriptions, (self.k, self.chroma_db, self.nkod_data_processor, self.language, self.embedding_provider, self.entity_generator, True)),
        ]
        num_workers = len(tasks)
        res = {}

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_name = {executor.submit(fn, *args): fn_name  for fn_name, fn, args in tasks}
            for future in as_completed(future_to_name):
                name = future_to_name[future]
                result = future.result()
                res[name] = result
        
        out_dfs = [res["matching_titles"], res["matching_descs"], res["matching_keywords"], res["entity_titles"], res["entity_keywords"], res["entity_descriptions"]]
        df = pd.concat(out_dfs, ignore_index=True)
        res_df = df.loc[df.groupby("dataset_uri")["score"].idxmin()]
        res_df = res_df.sort_values("score", ascending=True)
        return res_df

    def _run_reranking_parallel(self, matched_titles: list[dict], matched_descs: list[dict], matched_keywords: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
        tasks = [
            ("reranked_matching_titles", self.nkod_query_reranker.rerank_query_results, (self.query, matched_titles, self.llm_provider)),
            ("reranked_descs", self.nkod_query_reranker.rerank_query_results, (self.query, matched_descs, self.llm_provider)),
            ("reranked_keywords", self.nkod_query_reranker.rerank_query_results, (self.query, matched_keywords, self.llm_provider)),
        ]
        num_workers = len(tasks)
        res = {}

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_name = {executor.submit(fn, *args): fn_name for fn_name, fn, args in tasks}
            for future in as_completed(future_to_name):
                name = future_to_name[future]
                result = future.result()
                res[name] = result

        return res["reranked_matching_titles"], res["reranked_descs"], res["reranked_keywords"]

    def _run_reranking_ofn_batched(self, matched_df: pd.DataFrame) -> list[dict]:
        batched_df = [matched_df.iloc[i:i + self.BATCH_SIZE] for i in range(0, len(matched_df), self.BATCH_SIZE)]
        tasks = [
            (f"batch_{i}", self.nkod_query_reranker.rerank_query_results_ofn, (self.query, batch, self.llm_provider))
            for i, batch in enumerate(batched_df)
        ]
        
        results = {}
        with ThreadPoolExecutor(max_workers=100) as executor:
            future_to_name = {
                executor.submit(fn, *args): name
                for name, fn, args in tasks
            }
            for future in as_completed(future_to_name):
                name = future_to_name[future]
                results[name] = future.result()
        
        res = [item for sublist in results.values() for item in sublist]
        sorted_res = sorted(res, key=lambda d: d["relevance_score"], reverse=True)

        return sorted_res

    def _run_reranking_ofn_topk(self, matched_df: pd.DataFrame, k: int = 10) -> list[dict]:
        df_k = matched_df.iloc[:k].copy()
        df_rest = matched_df.iloc[k:].copy()
        df_rest["relevance_score"] = 0.0
        rest_list = df_rest.to_dict(orient="records")
        reranked_lst = self.nkod_query_reranker.rerank_query_results_ofn(self.query, df_k, self.llm_provider)
        reranked_lst.extend(rest_list)
        sorted_res = sorted(reranked_lst, key=lambda d: d["relevance_score"], reverse=True)

        return sorted_res


