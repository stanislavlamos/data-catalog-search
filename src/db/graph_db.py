import traceback
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from dotenv import load_dotenv
import os
import re


load_dotenv()

class GraphDb:

    GRAPHDB_URL_LOCAL = "http://localhost:7200/repositories"
    GRAPHDB_NAMED_GRAPH_TEMPLATE = "http%3A%2F%2Fexample.org%2F{}"
    GRAPHDB_NAMED_GRAPH_TEMPLATE_FROM = "<http://example.org/{}>"

    def __init__(self, catalog_name: str):
        self.repo_name = f"{catalog_name}_repo"
        self.GRAPHDB_USERNAME = os.getenv("GRAPH_DB_USER")
        self.GRAPHDB_PASSWORD = os.getenv("GRAPH_DB_PASSWORD")
        self.GRAPHDB_URL_REMOTE = os.getenv("GRAPH_DB_REPO")
        self.GRAPHDB_URL_REMOTE_UPDATE = os.getenv("GRAPH_DB_REPO_UPDATE")

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

    def add_new_namegraph_graphdb_remote(self, graph_iri: str, fpath: str, content_type: str):
        named_graph = self.GRAPHDB_NAMED_GRAPH_TEMPLATE.format(graph_iri)
        api_url = f"{self.GRAPHDB_URL_REMOTE}/rdf-graphs/service?graph={named_graph}"
        
        with open(fpath, 'rb') as f:
            data = f.read()

        headers = {
            "Content-Type": content_type 
        }

        if self.GRAPHDB_USERNAME is not None and self.GRAPHDB_PASSWORD is not None:
            response = requests.post(
                api_url,
                data=data,
                headers=headers,
                auth=(self.GRAPHDB_USERNAME, self.GRAPHDB_PASSWORD)
            )
        else:
            response = requests.post(
                api_url,
                data=data,
                headers=headers
            )

        correct_status_code = 204
        if response.status_code != correct_status_code:
            print(f"❌ API Error: Status code {response.status_code}, named graph: {named_graph}")
            print(f"Response text: {response.text}")
        
    def push_trig_to_graphdb_remote(self, file_path: str, graph_iri: str = "nkod-trig-graph") -> None:
        self.add_new_namegraph_graphdb_remote(
            graph_iri="nkod-trig-graph",
            fpath=file_path,
            content_type="application/trig"
        )
    
    def query_sparql_graphdb(self, query: str, named_graph_iris: list[str] | None = None) -> tuple[str | None, str | None]:
        """"
        Returns (error, query_result)
        """
        if named_graph_iris is not None:
            query = self.add_from_to_sparql(query, named_graph_iris)
        
        print(f"query with from: \n{query}\n")
        print("------------------------------------------------")
        
        api_url = self.GRAPHDB_URL_REMOTE
        headers = {
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/sparql-query",
        }
    
        try:
            if self.GRAPHDB_USERNAME is not None and self.GRAPHDB_PASSWORD is not None:
                response = requests.post(
                    api_url,
                    data=query,   
                    headers=headers,
                    auth=(self.GRAPHDB_USERNAME, self.GRAPHDB_PASSWORD)
                )
            else:
                response = requests.post(
                    api_url,
                    data=query,   
                    headers=headers,
                )

            #print(f"response from graphdb: {response}")

            correct_code = 200

            #print(f"response code: {response.status_code}")
            if response.status_code == correct_code:
                #print(f"response json: {response.json()}")
                return (None, response.json())

            #print(f"text response: {response.text}")
            return (response.text, None)

        except Exception as e:
            err = traceback.format_exc()
            #print(f"exception: {err}")
            return (err, None)
    
    def update_sparql_graphdb(self, query: str, named_graph_iris: list[str] | None = None) -> tuple[str | None, str | None]:
        """"
        Returns (error, query_result)
        """
        if named_graph_iris is not None:
            query = self.add_from_to_sparql(query, named_graph_iris)

        api_url = self.GRAPHDB_URL_REMOTE_UPDATE
        headers = {
            "Accept": "application/sparql-results+json",
            "Content-Type": "application/sparql-update",
        }
    
        try:
            if self.GRAPHDB_USERNAME is not None and self.GRAPHDB_PASSWORD is not None:
                response = requests.post(
                    api_url,
                    data=query,   
                    headers=headers,
                    auth=(self.GRAPHDB_USERNAME, self.GRAPHDB_PASSWORD)
                )
            else:
                response = requests.post(
                    api_url,
                    data=query,   
                    headers=headers,
                )

            correct_code = 200
            if response.status_code == correct_code:
                return (None, response.text)

            return (None, response.text)

        except Exception as e:
            err = traceback.format_exc()
            return (err, None)
    
    def add_from_to_sparql(self, query: str, named_graph_iris: list[str]) -> str:
        query_with_from_template = self.insert_from_clause_after_select(query)
        from_clauses = [f"FROM {self.GRAPHDB_NAMED_GRAPH_TEMPLATE_FROM.format(iri)}" for iri in named_graph_iris]
        from_clauses = '\n'.join(from_clauses)
        query_with_from = query_with_from_template.format(**({"FROM_CLAUSE": from_clauses}))

        return query_with_from

    def insert_from_clause_after_select(self, query_string: str, clause_to_insert: str = "{FROM_CLAUSE}"):
        query_string = query_string.replace('{', '{{').replace('}', '}}')
        normalized_query = re.sub(r'\s+', ' ', query_string).strip()
        pattern = r'(.*?)(SELECT\s+.*?)\s+WHERE\s*\{'
        match = re.search(pattern, normalized_query, re.IGNORECASE)
        
        if match:
            prefix_part = match.group(1).strip()
            select_part = match.group(2).strip()
            where_match = re.search(r'WHERE\s*\{', normalized_query[match.end(2):], re.IGNORECASE)

            if where_match:
                where_start_index = match.end(2) + where_match.start()
                
                transformed_query = (
                    f"{prefix_part}\n"  
                    f"{select_part}\n"  
                    f"{clause_to_insert}\n"  
                    f"{normalized_query[where_start_index:]}"
                )
                return transformed_query
            
        return query_string
