from typing import List
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
from src.models.base import BaseLLMProvider, BaseEmbeddingProvider


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, model_name: str, temperature: float):
        load_dotenv()
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def chat(self, user_prompt: str, system_prompt: str, user_prompt_vars: dict | None = None, structured_output: BaseModel | None = None) -> str:
        if structured_output is not None:
            self.llm = self.llm.with_structured_output(structured_output)

        user_prompt = user_prompt.format(**(user_prompt_vars or {}))
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self.llm.invoke(messages)

        return response


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.embeddings = OpenAIEmbeddings(model=model_name, dimensions=self.DEFAULT_DIMENSIONS)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)