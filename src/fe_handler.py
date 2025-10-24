import os
import requests
from typing import Dict, List, Any, Optional
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

def get_query_matching_datasets(query: str, llm_model: str, similarity_threshold: float = 0.7, max_results: int = 10) -> Dict[str, Any]:
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/match-datasets",
            json={
                "query": query,
                "llm_model": llm_model,
                "similarity_threshold": similarity_threshold,
                "max_results": max_results
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "datasets": []
        }


def generate_sparql(query: str, llm_model: str, selected_datasets: List[str]) -> Dict[str, Any]:
    """
    Generate SPARQL query from natural language using selected LLM.

    Args:
        query: Natural language query
        llm_model: Selected LLM model name
        selected_datasets: List of dataset IDs to include in SPARQL generation

    Returns:
        Dictionary containing generated SPARQL query and metadata
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/generate-sparql",
            json={
                "query": query,
                "llm_model": llm_model,
                "datasets": selected_datasets
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "sparql_query": None
        }


def execute_sparql(sparql_query: str) -> Dict[str, Any]:
    """
    Execute SPARQL query against NKOD endpoint.

    Args:
        sparql_query: SPARQL query string to execute

    Returns:
        Dictionary containing query results
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/execute-sparql",
            json={
                "sparql_query": sparql_query
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "results": []
        }


def submit_feedback(
    query: str,
    llm_model: str,
    sparql_query: str,
    feedback: str,
    rating: Optional[int] = None
) -> Dict[str, Any]:
    """
    Submit feedback for generated SPARQL query.

    Args:
        query: Original natural language query
        llm_model: LLM model used for generation
        sparql_query: Generated SPARQL query
        feedback: User feedback text
        rating: Optional rating (1-5)

    Returns:
        Dictionary containing submission status
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/submit-feedback",
            json={
                "query": query,
                "llm_model": llm_model,
                "sparql_query": sparql_query,
                "feedback": feedback,
                "rating": rating
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


def regenerate_sparql(
    query: str,
    llm_model: str,
    selected_datasets: List[str],
    previous_sparql: str,
    feedback: str
) -> Dict[str, Any]:
    """
    Regenerate SPARQL query based on user feedback.

    Args:
        query: Original natural language query
        llm_model: Selected LLM model name
        selected_datasets: List of dataset IDs
        previous_sparql: Previously generated SPARQL query
        feedback: User feedback for improvement

    Returns:
        Dictionary containing regenerated SPARQL query and metadata
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/regenerate-sparql",
            json={
                "query": query,
                "llm_model": llm_model,
                "datasets": selected_datasets,
                "previous_sparql": previous_sparql,
                "feedback": feedback
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "sparql_query": None
        }
