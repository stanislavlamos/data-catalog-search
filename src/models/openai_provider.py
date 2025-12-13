from typing import List
from langchain.schema import HumanMessage, SystemMessage
from openai import Omit, OpenAI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
from src.models.base import BaseLLMProvider, BaseEmbeddingProvider
from datetime import datetime
import time


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, model_name: str, temperature: float = 0.0):
        load_dotenv()
        self.temperature = temperature
        self.model_name = model_name

    def chat(self, user_prompt: str, system_prompt: str, user_prompt_vars: dict | None = None, system_prompt_vars: dict | None = None, structured_output: BaseModel | None = None, file_ids: list[str] | None = None, purpose: str | None = None, vector_store_id: str | None = None) -> str | BaseModel | tuple[str | BaseModel, str]:
        user_prompt = user_prompt.format(**(user_prompt_vars or {}))
        system_prompt = system_prompt.format(**(system_prompt_vars or {}))

        print(f"System: \n{system_prompt}\n\n")
        print(f"User: \n{user_prompt}\n\n")

        start = time.time()
        
        if file_ids is not None:
            return self.chat_vector_store(user_prompt, system_prompt, file_ids, purpose)

        if vector_store_id is not None:
            return self.resume_chat_vector_store(user_prompt, system_prompt, vector_store_id, purpose)

        effort = "minimal" if purpose is not None and purpose == "NKOD_RERANKING" else "low"
        reasoning = {"reasoning": {"effort": effort}} if self.model_name in ["gpt-5", "gpt-5-mini"] else {}
        llm = ChatOpenAI(model=self.model_name, temperature=self.temperature, **reasoning)
        if structured_output is not None:
            llm = llm.with_structured_output(structured_output)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages)

        end = time.time()
        print(f"Elapsed time: {end - start:.4f} seconds, model: {self.model_name}|effort: {effort}, purpose: {purpose}")
        return response
    
    def chat_vector_store(self, user_prompt: str, system_prompt: str, file_ids: list[str], purpose: str | None = None) -> tuple[str, str]:
        client = OpenAI()
        now = datetime.now()
        vs_name = f"vs_{now.strftime('%Y-%m-%d_%H-%M-%S')}"
        start = time.time()
        
        vector_store = client.vector_stores.create(
            name=vs_name,
            chunking_strategy=Omit(),
            file_ids=file_ids
        )
        print("vector store created")
        response = client.responses.create(
            model=self.model_name,
            reasoning={"effort": "low"},
            instructions=system_prompt,
            input=user_prompt,
            tools=[{
                "type": "file_search",
                "vector_store_ids": [f"{vector_store.id}"]
            }]
        )

        end = time.time()
        print(f"Elapsed time: {end - start:.4f} seconds, model: {self.model_name}|effort: low, purpose: {purpose}")
        return response.output_text, vector_store.id

    def resume_chat_vector_store(self, user_prompt: str, system_prompt: str, vector_store_id: str, purpose: str | None = None) -> tuple[str, str]:
        client = OpenAI()
        start = time.time()

        response = client.responses.create(
            model=self.model_name,
            reasoning={"effort": "low"},
            instructions=system_prompt,
            input=user_prompt,
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store_id]
            }]
        )

        end = time.time()
        print(f"Elapsed time: {end - start:.4f} seconds, model: {self.model_name}|effort: low, purpose: {purpose}")
        return response.output_text, vector_store_id


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str, dimensions: int | None = None):
        self.model_name = model_name
        self.embeddings = OpenAIEmbeddings(model=self.model_name, dimensions=dimensions)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)
    