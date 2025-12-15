from typing import List, Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.models.base import BaseEmbeddingProvider
from dotenv import load_dotenv


load_dotenv()

class GoogleEmbeddingProvider(BaseEmbeddingProvider):
    
    GOOGLE_TASK_TYPES = [
        "RETRIEVAL_DOCUMENT",
        "RETRIEVAL_QUERY",
        "SEMANTIC_SIMILARITY",
        "CLASSIFICATION",
        "CLUSTERING",
        "CODE_RETRIEVAL_DOCUMENT",
        "CODE_RETRIEVAL_QUERY",
    ]
    
    def __init__(self, model_name: str, output_dimensionality: Optional[int] = None):
        self.model_name = model_name

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.model_name, 
            output_dimensionality=output_dimensionality, 
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(
            texts=texts, 
            task_type="RETRIEVAL_DOCUMENT"
        )

    def embed_query(self, text: str) -> List[float]:
        return self.embeddings.embed_query(
            text=text, 
            task_type="RETRIEVAL_QUERY"
        )
    