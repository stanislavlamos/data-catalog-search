import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from dotenv import load_dotenv


load_dotenv()

class GraphDb:

    GRAPHDB_URL_LOCAL = "http://localhost:7200/repositories"
    GRAPHDB_URL_REMOTE = "http://osw.felk.cvut.cz:7200/repositories/lamossta"

    def __init__(self, catalog_name: str):
        self.repo_name = f"{catalog_name}_repo"

    def query_sparql(self, query: str, file_path: str):
        repo_url = f"{self.GRAPHDB_URL_LOCAL}/{self.repo_name}"

        response = requests.post(
            repo_url,
            data=query,
            headers={"Content-Type": "application/sparql-query",
                     "Accept": "application/sparql-results+json"}
        )

        return response.json()
    
    def query_test_local_repo(self, query: str):
        repo_url = f"{self.GRAPHDB_URL_LOCAL}/nkod-test-repo"

        response = requests.post(
            repo_url,
            data=query,
            headers={
                "Content-Type": "application/sparql-query",
                "Accept": "application/sparql-results+json"
            }
        )

        return response.json()
    
    def query_sparql_remote(self, query: str, endpoint: str) -> str:
        sparql = SPARQLWrapper(endpoint)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)
        results = sparql.query().convert()

        return results

    def add_new_namegraph(self, graph_iri: str, fpath: str, format: str):
        with open(fpath, 'rb') as f:
            data = f.read()
        

        headers = {
            "Content-Type": "text/turtle" 
        }
        
        print(f"Attempting to load data into graph: {NAMED_GRAPH} at {api_url}")
        
        try:
            response = requests.post(
                api_url,
                data=data,
                headers=headers,
                auth=(GRAPHDB_USERNAME, GRAPHDB_PASSWORD) # Basic Authentication
            )

            if response.status_code == 204:
                # 204 No Content is the standard success code for this operation
                print("✅ Success: Data loaded successfully into the named graph!")
            else:
                print(f"❌ API Error: Status code {response.status_code}")
                print(f"Response text: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Fatal connection error: {e}")
        
    def push_trig_to_repo(self, file_path: str) -> None:
        rdf_endpoint = f"{self.GRAPHDB_URL_LOCAL}/{self.repo_name}/statements"

        with open(file_path, "rb") as f:
            data = f.read()

        headers = {
            "Content-Type": "application/x-trig",
            'Accept': 'application/json'
        }

        response = requests.put(rdf_endpoint, headers=headers, data=data)


