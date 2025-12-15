from dotenv import load_dotenv
import cohere
import json


load_dotenv()

class CohereProvider:
    def __init__(self):
        self.client = cohere.ClientV2()
        self.model = "rerank-v4.0-pro"
    
    def rerank_docs(self, docs: list, top_n: int, query: str) -> dict:
        response = self.client.rerank(
            model="rerank-v4.0-pro",
            query=query,
            documents=docs,
            top_n=top_n,
        )
        
        return json.loads(response.json())
