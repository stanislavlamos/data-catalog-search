from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def chat(self, user_prompt: str, system_prompt: str, user_prompt_vars: dict | None = None, structured_output: BaseModel | None = None) -> str:
        """Chat interface for conversational models"""
        pass


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""

    DEFAULT_DIMENSIONS = 1024

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of queries"""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        pass