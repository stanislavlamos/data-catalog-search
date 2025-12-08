import pandas as pd
from src.models.base import BaseLLMProvider
from src.schemas.schemas import DatasetSelectionOutput
from src.prompts import nkod_query_matching_llm_judge_user, nkod_query_matching_llm_judge_system


class NkodQueryMatcherReranker:
    def rerank_query_results(self, query: str, matched_datasets: list[dict], llm_provider: BaseLLMProvider) -> list[dict]:
        datasets = "\n".join([f"{i + 1}. Doc: {d['doc']}\n   URI: {d['dataset_uri']}" for i, d in enumerate(matched_datasets)])

        llm_res = llm_provider.chat(
            user_prompt=nkod_query_matching_llm_judge_user["gpt-5"],
            user_prompt_vars={
                "user_query": query,
                "datasets": datasets
            },
            system_prompt=nkod_query_matching_llm_judge_system["gpt-5"],
            structured_output=DatasetSelectionOutput
        )
        
        sorted_datasets = self._sort_datasets_desc(llm_res, matched_datasets)
        return sorted_datasets
    
    def rerank_query_results_ofn(self, query: str, matched_datasets: pd.DataFrame, llm_provider: BaseLLMProvider) -> list[dict]:
        datasets = "\n".join([f"{idx + 1}. Doc: {row.title_cs} | {row.description_cs} | {row.publisher_cs}\n   URI: {row.dataset_uri}" for idx, row in enumerate(matched_datasets.itertuples(index=False))])

        llm_res = llm_provider.chat(
            user_prompt=nkod_query_matching_llm_judge_user["gpt-5"],
            user_prompt_vars={
                "user_query": query,
                "datasets": datasets,
                "n_datasets": matched_datasets.shape[0]
            },
            system_prompt=nkod_query_matching_llm_judge_system["gpt-5"],
            structured_output=DatasetSelectionOutput
        )
        
        sorted_datasets = self._sort_datasets_desc(llm_res, matched_datasets.to_dict(orient="records"))
        return sorted_datasets

    def _sort_datasets_desc(self, output: DatasetSelectionOutput, matched_datasets: list[dict]) -> list[dict]:
        ret_lst = []
        for sorted_dataset in output.datasets:
            current_matched_dataset = None

            for matched_dataset in matched_datasets:
                if sorted_dataset.uri == matched_dataset["dataset_uri"]:
                    current_matched_dataset = matched_dataset
                    break

            if current_matched_dataset is not None:
                current_matched_dataset["relevance_score"] = sorted_dataset.relevance_score
                ret_lst.append(current_matched_dataset)

        return  ret_lst
    