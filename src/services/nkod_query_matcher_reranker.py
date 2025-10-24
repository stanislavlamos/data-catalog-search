from src.models.base import BaseLLMProvider
from src.schemas.schemas import DatasetSelectionOutput
from src.prompts import nkod_query_matching_llm_judge_user, nkod_query_matching_llm_judge_system


class NkodQueryMatcherReranker:
    def rerank_query_results(self, query: str, merged_docs_with_uris: list[dict], llm_provider: BaseLLMProvider):
        datasets = "\n".join([f"{i + 1}. Doc: {d['doc']}\n   URI: {d['dataset_uri']}" for i, d in enumerate(merged_docs_with_uris)])

        llm_res = llm_provider.chat(
            user_prompt=nkod_query_matching_llm_judge_user["gpt-5"],
            user_prompt_vars={
                "user_query": query,
                "datasets": datasets
            },
            system_prompt=nkod_query_matching_llm_judge_system["gpt-5"],
            structured_output=DatasetSelectionOutput
        )
        sorted_datasets = self._sort_datasets_desc(llm_res)
        only_uris = [d[1] for d in sorted_datasets]

        return sorted_datasets, only_uris

    def _sort_datasets_desc(self, output: DatasetSelectionOutput) -> list[tuple]:
        sorted_datasets = sorted(
            output.datasets,
            key=lambda d: d.relevance_score,
            reverse=True
        )
        ret_lst = [(d.doc, d.uri) for d in sorted_datasets]

        return  ret_lst