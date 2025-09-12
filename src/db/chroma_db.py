from typing import List, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb import Documents, EmbeddingFunction, Embeddings
from ..models.base import BaseEmbeddingProvider


class ChromaDb:
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection_name = None
        self.collection = None
    
    def create_collection(self, collection_name: str, embedding_provider: BaseEmbeddingProvider, metadata: dict = {"hnsw:space": "cosine"}):
        self.collection_name = collection_name
        self.collection = self.client.create_collection(
            name=collection_name,
            metadata=metadata,
            embedding_function=ChromaEmbeddingFunction(embedding_provider)
        )

    def load_collection(self, collection_name: str, embedding_provider: BaseEmbeddingProvider):
        self.collection_name = collection_name
        self.collection = self.client.get_collection(self.collection_name, ChromaEmbeddingFunction(embedding_provider))

    def add_documents(self, texts: List[str], ids: list[str], metadatas: list[dict] | None = None) -> None:
        self.collection.add(
            documents=texts,
            metadatas=metadatas or [{} for _ in texts],
            ids=ids
        )

    def similarity_search(self, query_texts: List[str], k: int = 5) -> List[Tuple[str, str, float, dict]]:
        results = self.collection.query(
            query_texts=query_texts,
            n_results=k
        )

        documents = results['documents'][0]
        distances = results['distances'][0]
        metadatas = results['metadatas'][0]
        ids = results['ids'][0]

        return list(zip(ids, documents, distances, metadatas))

    def delete_collection(self, collection_name: str) -> None:
        self.client.delete_collection(name=collection_name)

    def list_collections(self) -> List[str]:
        collections = self.client.list_collections()
        return [collection.name for collection in collections]
    

class ChromaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, embedding_provider: BaseEmbeddingProvider):
        self.embedding_provider = embedding_provider
    
    def __call__(self, input: Documents) -> Embeddings:
        return self.embedding_provider.embed_documents(input)