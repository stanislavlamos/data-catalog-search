from concurrent.futures import ThreadPoolExecutor, as_completed
from src.db.chroma_db import ChromaDb
from src.models.model_handler import EmbeddingProviderHandler, LLMProviderHandler
from src.schemas.nkod_query_matcher_request import NkodQueryMatcherRequest
from src.schemas.nkod_query_matcher_response import NkodQueryMatcherResponse
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_query_matcher import NkodQueryMatcher
from src.services.nkod_query_matcher_reranker import NkodQueryMatcherReranker
import pandas as pd


class NkodQueryMatcherIntersectionPipeline:
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

    def run(self, request: NkodQueryMatcherRequest, with_keywords: bool) -> NkodQueryMatcherResponse:
        self.nkod_data_processor = NkodDataProcessor("nkod")
        self.chroma_db = ChromaDb(self.nkod_data_processor.vectordb_path)
        self.llm_provider = LLMProviderHandler().get_model(provider_name=request.llm_provider, model_name=request.model_name)
        self.embedding_provider = EmbeddingProviderHandler().get_model(provider_name=request.embedding_provider)
        self.language = request.language
        self.query = request.query
        self.nkod_query_matcher = NkodQueryMatcher(self.query)
        self.nkod_query_reranker = NkodQueryMatcherReranker()

        if with_keywords:
            df = self._run_query_matching_parallel()
            df_list = df.to_dict(orient="records")

            return NkodQueryMatcherResponse(
                matched_lst_dict=df_list
            )
        
        df = self._run_query_matching_parallel_no_keywords()
        df_list = df.to_dict(orient="records")

        return NkodQueryMatcherResponse(
            matched_lst_dict=df_list
        )
    
    def _run_query_matching_parallel(self) -> pd.DataFrame:
        tasks = [
            ("matching_titles", self.nkod_query_matcher.get_matching_titles, (self.k, self.chroma_db, self.nkod_data_processor, self.language, self.embedding_provider, True)),
            ("matching_descs", self.nkod_query_matcher.get_matching_descriptions, (self.k, self.chroma_db, self.nkod_data_processor, self.language, self.embedding_provider, True)),
            ("matching_keywords", self.nkod_query_matcher.get_matching_keywords, (self.k, self.chroma_db, self.nkod_data_processor, self.language, self.embedding_provider, True)),
            ("matching publishers", self.nkod_query_matcher.get_matching_publishers, (self.k, self.chroma_db, self.nkod_data_processor, self.language, self.embedding_provider, True)), 
        ]
        num_workers = len(tasks)
        res = {}

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_name = {executor.submit(fn, *args): fn_name  for fn_name, fn, args in tasks}
            for future in as_completed(future_to_name):
                name = future_to_name[future]
                result = future.result()
                res[name] = result
        
        out_dfs = [res["matching_titles"], res["matching_descs"], res["matching_keywords"], res["matching publishers"]]
        df = pd.concat(out_dfs, ignore_index=True)
        n_dfs = len(out_dfs)
        uri_counts = df["dataset_uri"].value_counts()
        valid_uris = uri_counts[uri_counts == n_dfs].index

        result_df = (
            df[df["dataset_uri"].isin(valid_uris)]
            .loc[lambda d: d.groupby("dataset_uri")["score"].idxmin()]
            .reset_index(drop=True)
        )        
        res_df = result_df.sort_values("score", ascending=True)

        return res_df
    
    def _run_query_matching_parallel_no_keywords(self) -> pd.DataFrame:
        tasks = [
            ("matching_titles", self.nkod_query_matcher.get_matching_titles, (self.k, self.chroma_db, self.nkod_data_processor, self.language, self.embedding_provider, True)),
            ("matching_descs", self.nkod_query_matcher.get_matching_descriptions, (self.k, self.chroma_db, self.nkod_data_processor, self.language, self.embedding_provider, True)),
            ("matching publishers", self.nkod_query_matcher.get_matching_publishers, (self.k, self.chroma_db, self.nkod_data_processor, self.language, self.embedding_provider, True)), 
        ]
        num_workers = len(tasks)
        res = {}

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_name = {executor.submit(fn, *args): fn_name  for fn_name, fn, args in tasks}
            for future in as_completed(future_to_name):
                name = future_to_name[future]
                result = future.result()
                res[name] = result
        
        out_dfs = [res["matching_titles"], res["matching_descs"], res["matching publishers"]]
        df = pd.concat(out_dfs, ignore_index=True)
        n_dfs = len(out_dfs)
        uri_counts = df["dataset_uri"].value_counts()
        valid_uris = uri_counts[uri_counts == n_dfs].index

        result_df = (
            df[df["dataset_uri"].isin(valid_uris)]
            .loc[lambda d: d.groupby("dataset_uri")["score"].idxmin()]
            .reset_index(drop=True)
        )        
        res_df = result_df.sort_values("score", ascending=True)

        return res_df
