from typing import List
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel
from dotenv import load_dotenv
from src.models.base import BaseLLMProvider, BaseEmbeddingProvider
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings


class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, model_name: str, temperature: float = 0.0):
        load_dotenv()
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)

    def chat(
        self,
        user_prompt: str,
        system_prompt: str,
        user_prompt_vars: dict | None = None,
        structured_output: BaseModel | None = None
    ) -> str:
        if structured_output is not None:
            self.llm = self.llm.with_structured_output(structured_output)

        user_prompt = user_prompt.format(**(user_prompt_vars or {}))
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self.llm.invoke(messages)
        return response


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=model_name,
            dimensions=self.DEFAULT_DIMENSIONS
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)
