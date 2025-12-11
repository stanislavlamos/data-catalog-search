from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.model_handler import LLMProviderHandler
from src.schemas.nkod_rag_request import NkodRagRequest
from src.schemas.nkod_rag_response import NkodRagResponse
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_rag import NkodRAG
from src.utils import delete_sparql_backticks, dir_name_from_uri


class NkodRagPipeline:
    def __init__(self, request: NkodRagRequest):
        self.llm_provider = LLMProviderHandler.get_model(request.provider_name, request.model_name)
        self.query = request.query
        self.matched_lst_dict = request.matched_lst_dict
        self.nkod_data_processor = NkodDataProcessor("nkod")
        self.model_name = request.model_name
        self.graph_db = GraphDb(self.nkod_data_processor.catalog_name)
        self.sq_lite = SqLite(self.nkod_data_processor.metadata_sql_path)
        self.language = request.language

    def run(self) -> NkodRagResponse:
        nkod_rag = NkodRAG()
        sparql_query = nkod_rag.generate_sparql_query(self.query, self.matched_lst_dict, self.llm_provider, self.model_name, self.nkod_data_processor, self.language, self.sq_lite, self.graph_db)
        sparql_query = delete_sparql_backticks(sparql_query)
        uris = [dir_name_from_uri(distribution["dataset_uri"]) for distribution in self.matched_lst_dict]

        try:
            error, query_result = self.graph_db.query_sparql_graphdb(sparql_query, uris)
            #print(f"{error}/{query_result}")
            if error is None:
                return NkodRagResponse(sparql_query=sparql_query, query_result=query_result)
            else:
                return NkodRagResponse(sparql_query=sparql_query, query_result=["TODO error loop"])                
        except Exception as e:
                return NkodRagResponse(sparql_query=sparql_query, query_result=["Exception"])                
    
    def error_loop(self):
        pass

    def parse_query_result(self):
        pass