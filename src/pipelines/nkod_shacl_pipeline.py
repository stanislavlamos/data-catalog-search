from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.model_handler import LLMProviderHandler
from src.schemas.nkod_shacl_response import NkodShaclResponse
from src.schemas.nkod_shacl_request import NkodShaclRequest
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_rdf_graph import NkodRdfGraph
from src.services.nkod_shacl import NkodShacl
from src.utils import delete_sparql_backticks


class NkodShaclPipeline:
    def __init__(self, request: NkodShaclRequest):
        self.llm_provider = LLMProviderHandler.get_model(request.provider_name, request.model_name)
        self.query = request.query
        self.dataset_uris = request.dataset_uris
        self.nkod_data_processor = NkodDataProcessor("nkod")
        self.model_name = request.model_name
        self.graph_db = GraphDb(self.nkod_data_processor.catalog_name)
        self.sq_lite = SqLite(self.nkod_data_processor.metadata_sql_path)
        self.language = request.language
    
    def run(self) -> NkodShaclResponse:
        nkod_shacl = NkodShacl()
        distributions = [self.nkod_data_processor.get_dataset_distributions(dataset_uri, self.graph_db) for dataset_uri in self.dataset_uris]
        sparql_query, distributions = nkod_shacl.generate_sparql_query(self.query, distributions, self.llm_provider, self.model_name, self.nkod_data_processor, self.dataset_uris, self.language, self.sq_lite, self.graph_db)
        sparql_query = delete_sparql_backticks(sparql_query)

        try:
            nkod_graph = NkodRdfGraph(distributions)
            query_result = nkod_graph.query_graph(sparql_query)
        except Exception as e:
            query_result = ["TODO error loop"]

        return NkodShaclResponse(sparql_query=sparql_query, query_result=query_result)
