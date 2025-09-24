import os.path
from datetime import date, datetime
from src.db.chroma_db import ChromaDb
from src.models.base import BaseEmbeddingProvider, BaseLLMProvider
from src.models.schemas import InputLanguage, TimeframeDetection, DatasetSelectionOutput
from src.prompts import timeframe_detection_user, timeframe_detection_system, nkod_query_mathching_llm_judge_user, \
    nkod_query_mathching_llm_judge_system
from src.services.base_query_matcher import BaseQueryMatcher
from src.services.nkod_data_processor import NkodDataProcessor
from src.utils import get_uris_from_chroma_query, load_jsonl_to_list, merge_chromadb_docs_with_metadatas, \
    get_relevance_score, get_uris_and_scores_from_chroma_query
import numpy as np
from itertools import product


class NkodQueryMatcher(BaseQueryMatcher):
    def __init__(self, query: str):
        self.query = query
        self.matching_keywords = []
        self.matching_descriptions = []
        self.matching_titles = []
        self.matching_distributions = []

    def high_k_intersection(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: InputLanguage, embedding_provider: BaseEmbeddingProvider) -> list:
        matching_titles = self.get_matching_titles(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_descriptions = self._get_matching_descriptions(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_keywords = self._get_matching_keywords(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_attributes = [matching_titles, matching_descriptions]#, matching_keywords]
        intersection = self.get_intersection(matching_attributes)

        return intersection

    def high_k_intersection_llm(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: InputLanguage, embedding_provider: BaseEmbeddingProvider, llm_provider: BaseLLMProvider) -> tuple[list[str], DatasetSelectionOutput]:
        matching_titles, merged_docs_with_metadatas = self.get_matching_titles_llm(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_descriptions = self._get_matching_descriptions(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_keywords = self._get_matching_keywords(k, chroma_db, nkod_data_processor, language.value, embedding_provider)
        matching_attributes = [matching_titles, matching_keywords, matching_descriptions]
        intersection = self.get_intersection(matching_attributes)
        datasets = "\n".join([f"{i + 1}. Title: {d['title']}\n   URI: {d['dataset_uri']}" for i, d in
                              enumerate(merged_docs_with_metadatas)])

        llm_res = llm_provider.chat(
            user_prompt=nkod_query_mathching_llm_judge_user["gpt-5"],
            user_prompt_vars={
                "user_query": self.query,
                "datasets": datasets
            },
            system_prompt=nkod_query_mathching_llm_judge_system["gpt-5"],
            structured_output=DatasetSelectionOutput
        )

        return intersection, llm_res

    def high_k_intersection_new_keywords(self, k: int):
        pass

    def get_matching_distributions(self):
        pass

    def _get_matching_keywords(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider, with_scores: bool = False) -> list[str] | tuple[list[str], list[tuple[float, str]]]:
        collection_name = f"{nkod_data_processor.keywords_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        similarity_search = chroma_db.similarity_search([self.query], k)
        query_result = get_uris_from_chroma_query(similarity_search["metadatas"])
        query_result_with_scores = get_uris_and_scores_from_chroma_query(similarity_search["documents"], similarity_search["distances"], "dataset_uri")

        if with_scores:
            return query_result, query_result_with_scores

        return query_result

    def _get_matching_descriptions(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider, with_scores: bool = False) -> list[str] | tuple[list[str], list[tuple[float, str]]]:
        collection_name = f"{nkod_data_processor.descriptions_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        similarity_search = chroma_db.similarity_search([self.query], k)
        query_result = get_uris_from_chroma_query(similarity_search["metadatas"])
        query_result_with_scores = get_uris_and_scores_from_chroma_query(similarity_search["documents"], similarity_search["distances"], "dataset_uri")

        if with_scores:
            return query_result, query_result_with_scores

        return query_result

    def get_matching_titles(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider, with_scores: bool = False) -> list[str] | tuple[list[str], list[tuple[float, str]]]:
        collection_name = f"{nkod_data_processor.titles_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        similarity_search = chroma_db.similarity_search([self.query], k)
        query_result = get_uris_from_chroma_query(similarity_search["metadatas"])
        query_result_with_scores = get_uris_and_scores_from_chroma_query(similarity_search["documents"], similarity_search["distances"], "dataset_uri")

        if with_scores:
            return query_result,query_result_with_scores

        return query_result

    def _get_matching_theme_labels(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider, with_scores: bool = False) -> list[str] | tuple[list[str], list[tuple[float, str]]]:
        collection_name = f"{nkod_data_processor.themes_labels_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        similarity_search = chroma_db.similarity_search([self.query], k)
        query_result = get_uris_from_chroma_query(similarity_search["metadatas"], "theme_name")
        query_result_with_scores = get_uris_and_scores_from_chroma_query(similarity_search["documents"], similarity_search["distances"], "theme_name")

        if with_scores:
            return query_result,query_result_with_scores

        return query_result

    def _get_matching_theme_definitions(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider, with_scores: bool = False) -> list[str] | tuple[list[str], list[tuple[float, str]]]:
        collection_name = f"{nkod_data_processor.themes_definitions_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        similarity_search = chroma_db.similarity_search([self.query], k)
        query_result = get_uris_from_chroma_query(similarity_search["metadatas"], "theme_name")
        query_result_with_scores = get_uris_and_scores_from_chroma_query(similarity_search["documents"], similarity_search["distances"], "theme_name")

        if with_scores:
            return query_result,query_result_with_scores

        return query_result

    def get_matching_titles_llm(self, k: int, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider, with_scores: bool = False) -> tuple[list[str], list[dict]]:
        collection_name = f"{nkod_data_processor.titles_collection_name}_{language}"
        chroma_db.load_collection(collection_name, embedding_provider)
        similarity_search_res = chroma_db.similarity_search([self.query], k)
        merged_docs_with_metadatas = merge_chromadb_docs_with_metadatas(similarity_search_res)
        query_result = get_uris_from_chroma_query(similarity_search_res["metadatas"])

        return query_result, merged_docs_with_metadatas

    def evaluate_on_ofn_dataset(self, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str, embedding_provider: BaseEmbeddingProvider):
        queries_dataset = load_jsonl_to_list("ofn_czech_matching_dataset.jsonl")
        k = 20

        for idx, dataset_item in enumerate(queries_dataset):
            self.query = dataset_item["query"].lower()
            cur_dataset = dataset_item["dataset_uris"][0] if len(dataset_item["dataset_uris"]) > 0 else ""
            print(f"Query {idx+1}/{len(queries_dataset)}")
            print(dataset_item)
            query_result_definitions, query_result_with_scores_definitions = self._get_matching_theme_definitions(k, chroma_db, nkod_data_processor, language, embedding_provider, True)
            query_result_labels, query_result_with_scores_labels = self._get_matching_theme_labels(k, chroma_db, nkod_data_processor, language, embedding_provider, True)
            query_result_titles, query_result_with_scores_titles = self.get_matching_titles(k, chroma_db, nkod_data_processor, language, embedding_provider, True)
            query_result_descriptions, query_result_with_scores_descriptions = self._get_matching_descriptions(k, chroma_db, nkod_data_processor, language, embedding_provider, True)
            query_result_keywords, query_result_with_scores_keywords= self._get_matching_keywords(k, chroma_db, nkod_data_processor, language, embedding_provider, True)

            print(f"In definitions: {cur_dataset in query_result_definitions}")
            print(f"Definitions similarity matching: {query_result_with_scores_definitions}")
            print(f"In labels: {cur_dataset in query_result_labels}")
            print(f"Labels similarity matching: {query_result_with_scores_labels}")
            print(f"In titles: {cur_dataset in query_result_titles}")
            print(f"Titles similarity matching: {query_result_with_scores_titles}")
            print(f"In descriptions: {cur_dataset in query_result_descriptions}")
            print(f"Descriptions similarity matching: {query_result_with_scores_descriptions}")
            print(f"In keywords: {cur_dataset in query_result_keywords}")
            print(f"Keywords similarity matching: {query_result_with_scores_keywords}")
            print("\n\n")

    def get_intersection(self, input_lists: list[list]) -> list:
        return list(set(input_lists[0]).intersection(*map(set, input_lists[1:])))

    def evaluate_high_k_intersection(self, log_path: str, nkod_data_processor: NkodDataProcessor, language: str, intersections: list[list], matching_titles: list[list]) -> dict:
        if language == InputLanguage.ENGLISH.value:
            fpath = os.path.join(nkod_data_processor.data_path, "nkod_query_matching_dataset_simple_en.jsonl")
        else: # language == InputLanguage.CZECH
            fpath = os.path.join(nkod_data_processor.data_path, "nkod_query_matching_dataset_simple_cs.jsonl")

        list_of_queries = load_jsonl_to_list(fpath)
        n_queries = len(list_of_queries)
        intersection_matches = np.zeros(n_queries)
        titles_matches = np.zeros(n_queries)

        with open(log_path, "w", encoding="utf-8") as f:
            for idx, query_dict in enumerate(list_of_queries):
                query = query_dict["query"]
                dataset_uri = query_dict["dataset_uri"]
                in_intersection = False
                in_matching_titles = False

                if dataset_uri in intersections[idx]:
                    intersection_matches[idx] = 1
                    in_intersection = True

                if dataset_uri in matching_titles[idx]:
                    titles_matches[idx] = 1
                    in_matching_titles = True

                f.write(f"Query {idx+1}/{n_queries}\n")
                f.write(f"Query: {query}\n")
                f.write(f"In intersection: {in_intersection}\n")
                f.write(f"In matching titles: {in_matching_titles}\n")
                f.write(f"Dataset uri: {dataset_uri}\n")
                f.write(f"Matching titles: {matching_titles[idx]}\n")
                f.write(f"Intersections: {intersections[idx]}\n")
                f.write("\n\n")

            f.write("\n\n")
            f.write("Final stats\n")
            f.write(f"Number of queries: {n_queries}\n")
            f.write(f"Total number of matches in intersections: {np.sum(intersection_matches)}\n")
            f.write(f"Mean number of matches in intersections: {intersection_matches.mean()}\n")
            f.write(f"Total number of matches in titles: {np.sum(titles_matches)}\n")
            f.write(f"Mean number of matches in titles: {titles_matches.mean()}\n")

        return {
            "number_of_queries": n_queries,
            "total_matches_intersections": int(np.sum(intersection_matches)),
            "mean_matches_intersections": float(intersection_matches.mean()),
            "total_matches_titles": int(np.sum(titles_matches)),
            "mean_matches_titles": float(titles_matches.mean()),
        }


    def evaluate_high_k_intersection_llm(self, log_path: str, nkod_data_processor: NkodDataProcessor, language: str, intersections: list[list], matching_titles: list[list], llm_res: list[DatasetSelectionOutput]) -> dict:
        if language == InputLanguage.ENGLISH.value:
            fpath = os.path.join(nkod_data_processor.data_path, "nkod_query_matching_dataset_simple_en.jsonl")
        else: # language == InputLanguage.CZECH
            fpath = os.path.join(nkod_data_processor.data_path, "nkod_query_matching_dataset_simple_cs.jsonl")

        list_of_queries = load_jsonl_to_list(fpath)
        n_queries = len(list_of_queries)
        intersection_matches = np.zeros(n_queries)
        titles_matches = np.zeros(n_queries)
        llm_scores = np.zeros(n_queries)

        with open(log_path, "w", encoding="utf-8") as f:
            for idx, query_dict in enumerate(list_of_queries):
                query = query_dict["query"]
                dataset_uri = query_dict["dataset_uri"]
                in_intersection = False
                in_matching_titles = False
                llm_scores[idx] = get_relevance_score(llm_res[idx], dataset_uri)

                if dataset_uri in intersections[idx]:
                    intersection_matches[idx] = 1
                    in_intersection = True

                if dataset_uri in matching_titles[idx]:
                    titles_matches[idx] = 1
                    in_matching_titles = True

                f.write(f"Query {idx+1}/{n_queries}\n")
                f.write(f"Query: {query}\n")
                f.write(f"In intersection: {in_intersection}\n")
                f.write(f"In matching titles: {in_matching_titles}\n")
                f.write(f"Current LLM score: {llm_scores[idx]}\n")
                f.write(f"Dataset uri: {dataset_uri}\n")
                f.write(f"Matching titles: {matching_titles[idx]}\n")
                f.write(f"Intersections: {intersections[idx]}\n")
                f.write(f"LLM scores: {llm_res[idx]}\n")
                f.write("\n\n")

            f.write("\n\n")
            f.write("Final stats\n")
            f.write(f"Number of queries: {n_queries}\n")
            f.write(f"Total number of matches in intersections: {np.sum(intersection_matches)}\n")
            f.write(f"Mean number of matches in intersections: {intersection_matches.mean()}\n")
            f.write(f"Total number of matches in titles: {np.sum(titles_matches)}\n")
            f.write(f"Mean number of matches in titles: {titles_matches.mean()}\n")
            f.write(f"Mean LLM score: {llm_scores.mean()}\n")

        return {
            "number_of_queries": n_queries,
            "total_matches_intersections": int(np.sum(intersection_matches)),
            "mean_matches_intersections": float(intersection_matches.mean()),
            "total_matches_titles": int(np.sum(titles_matches)),
            "mean_matches_titles": float(titles_matches.mean()),
            "mean_llm_score": float(llm_scores.mean())
        }

    def run_best_k_search(self, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, embedding_provider: BaseEmbeddingProvider, language: InputLanguage) -> list[dict]:
        ks_intersection = [40]#[10, 20, 30, 40, 50]
        ks_titles = [10]#[3, 5, 10, 15]
        k_combinations = list(product(ks_intersection, ks_titles))
        queries = load_jsonl_to_list(os.path.join(nkod_data_processor.data_path, f"nkod_query_matching_dataset_simple_{language.value}.jsonl"))
        results = []

        for k_intersection, k_titles in k_combinations:
            intersections = []
            matching_titles = []
            log_path = os.path.join(nkod_data_processor.data_path, f"res_{language}_{k_intersection}_{k_titles}_{datetime.now().date().isoformat()}.txt")

            for query in queries:
                self.query = query["query"]
                intersections.append(self.high_k_intersection(k_intersection, chroma_db, nkod_data_processor, language, embedding_provider))
                matching_titles.append(self.get_matching_titles(k_titles, chroma_db, nkod_data_processor, language.value, embedding_provider))

            result = self.evaluate_high_k_intersection(log_path, nkod_data_processor, language.value, intersections, matching_titles)
            results.append(result)

        return results

    def run_best_k_search_llm(self, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, embedding_provider: BaseEmbeddingProvider, language: InputLanguage, llm_provider: BaseLLMProvider) -> list[dict]:
        ks_intersection = [40]#[10, 20, 30, 40, 50]
        ks_titles = [5]#[3, 5, 10, 15]
        k_combinations = list(product(ks_intersection, ks_titles))
        queries = load_jsonl_to_list(os.path.join(nkod_data_processor.data_path, f"nkod_query_matching_dataset_simple_{language.value}.jsonl"))
        results = []

        for k_intersection, k_titles in k_combinations:
            intersections = []
            matching_titles = []
            llm_reses = []
            log_path = os.path.join(nkod_data_processor.data_path, f"res_{language.value}_{k_intersection}_{k_titles}_{datetime.now().date().isoformat()}")

            for query in queries:
                self.query = query["query"]
                intersection, llm_res = self.high_k_intersection_llm(k_intersection, chroma_db, nkod_data_processor, language, embedding_provider, llm_provider)
                intersections.append(intersection)
                llm_reses.append(llm_res)
                matching_titles.append(self.get_matching_titles(k_titles, chroma_db, nkod_data_processor, language.value, embedding_provider))

            result = self.evaluate_high_k_intersection_llm(log_path, nkod_data_processor, language.value, intersections, matching_titles, llm_reses)
            results.append(result)

        return results


