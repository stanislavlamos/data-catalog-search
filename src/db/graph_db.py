import requests
from SPARQLWrapper import SPARQLWrapper, JSON


class GraphDb:

    GRAPHDB_URL = "http://localhost:7200/repositories"

    def __init__(self, catalog_name: str):
        self.repo_name = f"{catalog_name}_repo"

    def query_sparql(self, query: str, file_path: str):
        repo_url = f"{self.GRAPHDB_URL}/{self.repo_name}"

        response = requests.post(
            repo_url,
            data=query,
            headers={"Content-Type": "application/sparql-query",
                     "Accept": "application/sparql-results+json"}
        )

        return response.json()
    
    def query_sparql_remote(self, query: str, endpoint: str) -> str:
        sparql = SPARQLWrapper(endpoint)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        results = sparql.query().convert()

        return results
    
    def push_trig_to_repo(self, file_path: str) -> None:
        rdf_endpoint = f"{self.GRAPHDB_URL}/{self.repo_name}/statements"

        with open(file_path, "rb") as f:
            data = f.read()

        headers = {
            "Content-Type": "application/x-trig",
            'Accept': 'application/json'
        }

        response = requests.put(rdf_endpoint, headers=headers, data=data)


