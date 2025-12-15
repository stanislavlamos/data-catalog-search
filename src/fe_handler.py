from concurrent.futures import ThreadPoolExecutor
import os
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv
from src.pipelines.all_datasets_pipeline import AllDatasetsPipeline
from src.pipelines.language_detection_pipeline import LanguageDetectionPipeline
from src.pipelines.nkod_graph_sparql_pipeline import NkodGraphSparqlPipeline
from src.pipelines.nkod_openai_files_pipeline import NkodOpenAiFilesPipeline
from src.pipelines.nkod_query_matcher_pipeline import NkodQueryMatcherPipeline
from src.pipelines.nkod_rag_pipeline import NkodRagPipeline
from src.pipelines.nkod_shacl_pipeline import NkodShaclPipeline
from src.pipelines.timeframe_detection_pipeline import TimeframeDetectionPipeline
from src.schemas.language_detection_request import LanguageDetectionRequest
from src.schemas.nkod_graph_sparql_request import NkodGraphSparqlRequest
from src.schemas.nkod_openai_files_request import NkodOpenAiFilesRequest
from src.schemas.nkod_query_matcher_request import NkodQueryMatcherRequest
from src.schemas.nkod_rag_request import NkodRagRequest
from src.schemas.nkod_shacl_request import NkodShaclRequest
from src.schemas.timeframe_detection_request import TimeframeDetectionRequest


load_dotenv()
API_BASE_URL = os.getenv('API_BASE_URL')

def get_timeframe(query: str, llm_provider: str, model_name: str) -> Dict[str, Any]:
    """
    response = requests.post(
        f"{API_BASE_URL}/detect-timeframe",
        json={
            "text": query,
            "model_name": "gpt-4.1-nano",
            "llm_provider": llm_provider
        }
    )
    response.raise_for_status()
    """
    input_dict = {
        "text": query,
        "model_name": "gpt-4.1",
        "llm_provider": llm_provider
    }
    res = TimeframeDetectionPipeline().run(TimeframeDetectionRequest(**input_dict)).model_dump()
    return res


def get_language(query: str, llm_provider: str, model_name: str) -> Dict[str, Any]:
    """
    response = requests.post(
        f"{API_BASE_URL}/detect-language",
        json={
            "text": query,
            "model_name": "gpt-4.1-nano",
            "llm_provider": llm_provider
        }
    )
    response.raise_for_status()
    """
    input_dict = {
        "text": query,
        "model_name": "gpt-4.1-nano",
        "llm_provider": llm_provider
    }
    res = LanguageDetectionPipeline().run(LanguageDetectionRequest(**input_dict)).model_dump()
    return res


def get_query_matching_datasets(query: str, llm_provider: str, model_name: str, language: str) -> Dict[str, Any]:
    """
    response = requests.post(
        f"{API_BASE_URL}/match-query",
        json={
            "query": query,
            "llm_provider": llm_provider,
            "model_name": "gpt-4.1",
            "language": language
        }
    )
    response.raise_for_status()
    """
    input_dict = {
        "query": query,
        "llm_provider": llm_provider,
        "model_name": "gpt-5",
        "language": language
    }
    res = NkodQueryMatcherPipeline().run(NkodQueryMatcherRequest(**input_dict)).model_dump()
    return res


def get_all_datasets() -> List[Dict[str, Any]]:
    """
    response = requests.get(f"{API_BASE_URL}/get-all-datasets")
    response.raise_for_status()
    """
    res = AllDatasetsPipeline().run().model_dump()
    return res


def query_matching_content(query: str, llm_provider: str, model_name: str, language: str) -> tuple[Dict[str, Any], list[Dict[str, Any]]]:
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_query = executor.submit(get_query_matching_datasets, query, llm_provider, model_name, language)
        future_all = executor.submit(get_all_datasets)
        
        matching_query_result = future_query.result()
        all_datasets_result = future_all.result()
    
    return matching_query_result, all_datasets_result    


def generate_sparql(query: str, model_name: str, selected_datasets: List[str], language: str) -> Dict[str, Any]:
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_graph = executor.submit(get_graph_sparql_response, query, model_name, selected_datasets, language)
        future_rag = executor.submit(get_rag_response, query, model_name, selected_datasets, language)
        future_openai_files = executor.submit(get_openai_files_response, query, model_name, selected_datasets, language)
        future_shacl = executor.submit(get_shacl_response, query, model_name, selected_datasets, language)      

        graph_result = future_graph.result()
        rag_result = future_rag.result()
        openai_files_result = future_openai_files.result()
        shacl_result = future_shacl.result()

    return {
        "graph_sparql": graph_result,
        "rag": rag_result,
        "openai_files": openai_files_result,
        "shacl": shacl_result
    }
    """
    graph_result = get_graph_sparql_response(query, model_name, selected_datasets, language)
    rag_result = get_rag_response(query, model_name, selected_datasets, language)
    openai_files = get_openai_files_response(query, model_name, selected_datasets, language)
    shacl_result = get_shacl_response(query, model_name, selected_datasets, language)
    
    return {
        "graph_sparql": graph_result,
        "rag": rag_result,
        "openai_files": openai_files,
        "shacl": shacl_result
    }
    """


def get_graph_sparql_response(query: str, model_name: str, dataset_uris: List[str], language: str) -> Dict[str, Any]:
    """
    response = requests.post(
        f"{API_BASE_URL}/nkod-graph-sparql",
        json={
            "query": query,
            "model_name": model_name,
            "matched_lst_dict": dataset_uris,
            "language": language
        }
    )
    response.raise_for_status()

    return response.json()
    """
    json_dict = {
        "query": query,
        "model_name": model_name,
        "matched_lst_dict": dataset_uris,
        "language": language
    }
    res = NkodGraphSparqlPipeline(NkodGraphSparqlRequest(**json_dict)).run().model_dump()
    return res


def get_rag_response(query: str, model_name: str, dataset_uris: List[str], language: str) -> Dict[str, Any]:
    """
    response = requests.post(
        f"{API_BASE_URL}/nkod-rag",
        json={
            "query": query,
            "model_name": model_name,
            "matched_lst_dict": dataset_uris,
            "language": language
        }
    )
    response.raise_for_status()

    return response.json()
    """
    json_dict = {
        "query": query,
        "model_name": model_name,
        "matched_lst_dict": dataset_uris,
        "language": language
    }
    res = NkodRagPipeline(NkodRagRequest(**json_dict)).run().model_dump()
    return res


def get_openai_files_response(query: str, model_name: str, dataset_uris: List[str], language: str) -> Dict[str, Any]:
    """
    response = requests.post(
        f"{API_BASE_URL}/nkod-openai-files",
        json={
            "query": query,
            "model_name": model_name,
            "matched_lst_dict": dataset_uris,
            "language": language
        }
    )
    response.raise_for_status()

    return response.json()
    """
    json_dict = {
        "query": query,
        "model_name": model_name,
        "matched_lst_dict": dataset_uris,
        "language": language
    }
    res = NkodOpenAiFilesPipeline(NkodOpenAiFilesRequest(**json_dict)).run().model_dump()
    return res


def get_shacl_response(query: str, model_name: str, dataset_uris: List[str], language: str) -> Dict[str, Any]:
    """
    response = requests.post(
        f"{API_BASE_URL}/nkod-shacl",
        json={
            "query": query,
            "model_name": model_name,
            "matched_lst_dict": dataset_uris,
            "language": language
        }
    )
    response.raise_for_status()

    return response.json()
    """
    json_dict = {
        "query": query,
        "model_name": model_name,
        "matched_lst_dict": dataset_uris,
        "language": language
    }
    res = NkodShaclPipeline(NkodShaclRequest(**json_dict)).run().model_dump()
    return res
