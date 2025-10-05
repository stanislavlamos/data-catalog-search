from datetime import datetime
from itertools import product
from src.db.chroma_db import ChromaDb
from src.models.base import BaseEmbeddingProvider, BaseLLMProvider
from src.models.schemas import InputLanguage, DatasetSelectionOutput
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_query_matcher import NkodQueryMatcher
import numpy as np
import os
from src.services.nkod_query_matcher_reranker import NkodQueryMatcherReranker
from src.utils import load_jsonl_to_list, get_relevance_score, clean_text, get_overlap_info, merge_lst_with_tuple_lst


class NkodQueryMatcherEvaluator(NkodQueryMatcher):
    def __init__(self, query: str = ""):
        super().__init__(query)
        self.nkod_evaluation_path = os.path.join(self.data_path, "evaluation")

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

    def evaluate_on_ofn_dataset(self, k: int, ofn_dataset_fname: str, chroma_db: ChromaDb, nkod_data_processor: NkodDataProcessor, language: str,
                                embedding_provider: BaseEmbeddingProvider, nkod_reranker: NkodQueryMatcherReranker, llm_provider: BaseLLMProvider):
        queries_dataset = load_jsonl_to_list(os.path.join(nkod_data_processor.data_path, ofn_dataset_fname))

        for idx, dataset_item in enumerate(queries_dataset):
            self.query = clean_text(dataset_item["query"])
            cur_dataset = dataset_item["dataset_uris"] if len(dataset_item["dataset_uris"]) > 0 else []
            print(f"Query {idx + 1}/{len(queries_dataset)}")
            print(f"Desc: {dataset_item['desc']}")
            print(f"Original query: {dataset_item['query']}")
            print(f"Cleaned query: {self.query}")


            query_result_titles, query_result_with_scores_titles = self.get_matching_titles(k, chroma_db,
                                                                                            nkod_data_processor,
                                                                                            language,
                                                                                            embedding_provider, True)
            uris_and_titles = merge_lst_with_tuple_lst(query_result_titles, query_result_with_scores_titles)
            reranked_titles_and_uris, uris_titles_reranked = nkod_reranker.rerank_query_results(self.query, uris_and_titles, llm_provider)

            query_result_descriptions, query_result_with_scores_descriptions = self.get_matching_descriptions(k,
                                                                                                              chroma_db,
                                                                                                              nkod_data_processor,
                                                                                                              language,
                                                                                                              embedding_provider,
                                                                                                              True)
            uris_and_descs = merge_lst_with_tuple_lst(query_result_descriptions, query_result_with_scores_descriptions)
            reranked_descs_and_uris, uris_desc_reranked = nkod_reranker.rerank_query_results(self.query, uris_and_descs, llm_provider)

            query_result_keywords, query_result_with_scores_keywords = self.get_matching_keywords(k, chroma_db,
                                                                                                  nkod_data_processor,
                                                                                                  language,
                                                                                                  embedding_provider,
                                                                                                  True)
            uris_and_keywords = merge_lst_with_tuple_lst(query_result_keywords, query_result_with_scores_keywords)
            reranked_keywords_and_uris, uris_keywords_reranked = nkod_reranker.rerank_query_results(self.query, uris_and_keywords, llm_provider)

            print(f"In titles: {get_overlap_info(cur_dataset, query_result_titles)}")
            print(f"In titles reranked{get_overlap_info(cur_dataset, uris_titles_reranked)}")
            print(f"Titles similarity matching: {query_result_with_scores_titles}")
            print("\n")
            print(f"In descriptions: {get_overlap_info(cur_dataset, query_result_descriptions)}")
            print(f"In descriptions reranked: {get_overlap_info(cur_dataset, uris_desc_reranked)}")
            print(f"Descriptions similarity matching: {query_result_with_scores_descriptions}")
            print("\n")
            print(f"In keywords: {get_overlap_info(cur_dataset, query_result_keywords)}")
            print(f"In keywords reranked: {get_overlap_info(cur_dataset, uris_keywords_reranked)}")
            print(f"Keywords similarity matching: {query_result_with_scores_keywords}")
            print("----------------------------------------------------------------")
            print("\n\n")

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
