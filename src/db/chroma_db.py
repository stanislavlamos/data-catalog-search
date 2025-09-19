from typing import List
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb import Documents, EmbeddingFunction, Embeddings
from ..models.base import BaseEmbeddingProvider
from typing import Generator
from tqdm import tqdm


class ChromaDb:
    def __init__(self, persist_directory: str):
        self.flush_cache()

        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection_name = None
        self.collection = None
    
    def create_collection(self, collection_name: str, embedding_provider: BaseEmbeddingProvider, metadata: dict = {"hnsw:space": "cosine"}):
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata=metadata,
            embedding_function=ChromaEmbeddingFunction(embedding_provider)
        )

        print(f"Created or loaded collection '{collection_name}'")

    def load_collection(self, collection_name: str, embedding_provider: BaseEmbeddingProvider):
        self.collection_name = collection_name
        self.collection = self.client.get_collection(self.collection_name, ChromaEmbeddingFunction(embedding_provider))

    def add_documents(self, texts: list[str], ids: list[str], metadatas: list[dict] | None = None) -> None:
        self.collection.add(
            documents=texts,
            metadatas=metadatas or [{} for _ in texts],
            ids=ids
        )

    def add_documents_batched(self, texts: Generator[list[str], None, None], ids: Generator[list[str], None, None], metadatas: Generator[list[dict], None, None], property_name: str, num_batches: int) -> None:
        for text_batch, id_batch, metadatas_batch in tqdm(
            zip(texts, ids, metadatas),
            desc=f"Adding document batches of {property_name}",
            total=num_batches
        ):
            self.collection.add(
                documents=text_batch,
                metadatas=metadatas_batch,
                ids=id_batch
            )

    def similarity_search(self, query_texts: List[str], k: int = 5) -> list[dict]:
        results = self.collection.query(
            query_texts=query_texts,
            n_results=k
        )

        return results

    def delete_collection(self, collection_name: str) -> None:
        self.client.delete_collection(name=collection_name)

    def list_collections(self) -> List[str]:
        return self.client.list_collections()

    def flush_cache(self) -> None:
        chromadb.api.client.SharedSystemClient.clear_system_cache()


class ChromaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, embedding_provider: BaseEmbeddingProvider):
        self.embedding_provider = embedding_provider
    
    def __call__(self, input: Documents) -> Embeddings:
        return self.embedding_provider.embed_documents(input)