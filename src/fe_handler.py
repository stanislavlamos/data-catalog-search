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
    print("Response received from /match-query endpoint.")
    print(response.json())
    
    return response.json()

def generate_sparql(query: str, llm_model: str, selected_datasets: List[str]) -> Dict[str, Any]:
    pass
