from typing import List
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
from src.models.base import BaseLLMProvider, BaseEmbeddingProvider


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, model_name: str, temperature: float = 1.0):
        load_dotenv()
        self.temperature = temperature
        self.model_name = model_name

    def chat(self, user_prompt: str, system_prompt: str, user_prompt_vars: dict | None = None, system_prompt_vars: dict | None = None, structured_output: BaseModel | None = None, file_ids: list[str] | None = None) -> str | BaseModel:
        llm = ChatOpenAI(model=self.model_name, temperature=self.temperature)

        if structured_output is not None:
            llm = llm.with_structured_output(structured_output)

        user_prompt = user_prompt.format(**(user_prompt_vars or {}))
        system_prompt = system_prompt.format(**(system_prompt_vars or {}))

        if file_ids is not None:
            human_message_content = [
                {"type": "text", "text": user_prompt},
                *[{"type": "file", "file_id": fid} for fid in file_ids]
            ]
        else:
            human_message_content = user_prompt

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message_content)
        ]
        response = llm.invoke(messages)

        return response


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str, dimensions: int | None = None):
        self.model_name = model_name
        self.embeddings = OpenAIEmbeddings(model=self.model_name, dimensions=dimensions)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)
    