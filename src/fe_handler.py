from concurrent.futures import ThreadPoolExecutor
import os
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv


load_dotenv()
API_BASE_URL = os.getenv('API_BASE_URL')

def get_timeframe(query: str, llm_provider: str, model_name: str) -> Dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/detect-timeframe",
        json={
            "text": query,
            "model_name": model_name,
            "llm_provider": llm_provider
        }
    )
    response.raise_for_status()

    return response.json()


def get_language(query: str, llm_provider: str, model_name: str) -> Dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/detect-language",
        json={
            "text": query,
            "model_name": model_name,
            "llm_provider": llm_provider
        }
    )
    response.raise_for_status()

    return response.json()


def get_query_matching_datasets(query: str, llm_provider: str, model_name: str, language: str) -> Dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/match-query",
        json={
            "query": query,
            "llm_provider": llm_provider,
            "model_name": model_name,
            "language": language
        }
    )
    response.raise_for_status()
    
    return response.json()


def get_all_datasets() -> List[Dict[str, Any]]:
    response = requests.get(f"{API_BASE_URL}/get-all-datasets")
    response.raise_for_status()
    
    return response.json()


def query_matching_content(query: str, llm_provider: str, model_name: str, language: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_query = executor.submit(get_query_matching_datasets, query, llm_provider, model_name, language)
        future_all = executor.submit(get_all_datasets)
        
        matching_query_result = future_query.result()
        all_datasets_result = future_all.result()
    
    return matching_query_result, all_datasets_result    


def generate_sparql(query: str, model_name: str, selected_datasets: List[str], language: str) -> Dict[str, Any]:   
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_graph = executor.submit(get_graph_sparql_response, query, model_name, selected_datasets, language)
        future_rag = executor.submit(get_rag_response, query, model_name, selected_datasets, language)
        future_openai_files = executor.submit(get_openai_files_response, query, model_name, selected_datasets, language)        

        graph_result = future_graph.result()
        rag_result = future_rag.result()
        openai_files_result = future_openai_files.result()

    return {
        "graph_sparql": graph_result,
        "rag": rag_result,
        "openai_files": openai_files_result
    }
    """
    graph_result = get_graph_sparql_response(query, model_name, selected_datasets, language)
    rag_result = get_rag_response(query, model_name, selected_datasets, language)
    openai_files = get_openai_files_response(query, model_name, selected_datasets, language)
    


    return {
        "graph_sparql": graph_result,
        "rag": rag_result,
        "openai_files": openai_files
    }
    """

def get_graph_sparql_response(query: str, model_name: str, dataset_uris: List[str], language: str) -> Dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/nkod-graph-sparql",
        json={
            "query": query,
            "model_name": model_name,
            "dataset_uris": dataset_uris,
            "language": language
        }
    )
    response.raise_for_status()

    return response.json()


def get_rag_response(query: str, model_name: str, dataset_uris: List[str], language: str) -> Dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/nkod-rag",
        json={
            "query": query,
            "model_name": model_name,
            "dataset_uris": dataset_uris,
            "language": language
        }
    )
    response.raise_for_status()

    return response.json()


def get_openai_files_response(query: str, model_name: str, dataset_uris: List[str], language: str) -> Dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/nkod-openai-files",
        json={
            "query": query,
            "model_name": model_name,
            "dataset_uris": dataset_uris,
            "language": language
        }
    )
    response.raise_for_status()

    return response.json()

