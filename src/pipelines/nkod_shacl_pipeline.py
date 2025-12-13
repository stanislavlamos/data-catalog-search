from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.model_handler import LLMProviderHandler
from src.schemas.nkod_shacl_response import NkodShaclResponse
from src.schemas.nkod_shacl_request import NkodShaclRequest
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_shacl import NkodShacl
from src.utils import delete_sparql_backticks, dir_name_from_uri


class NkodShaclPipeline:
    def __init__(self, request: NkodShaclRequest):
        self.llm_provider = LLMProviderHandler.get_model(request.provider_name, request.model_name)
        self.query = request.query
        self.matched_lst_dict = request.matched_lst_dict
        self.nkod_data_processor = NkodDataProcessor("nkod")
        self.model_name = request.model_name
        self.graph_db = GraphDb(self.nkod_data_processor.catalog_name)
        self.sq_lite = SqLite(self.nkod_data_processor.metadata_sql_path)
        self.language = request.language
    
    def run(self) -> NkodShaclResponse:
        nkod_shacl = NkodShacl()
        sparql_query = nkod_shacl.generate_sparql_query(self.query, self.matched_lst_dict, self.llm_provider, self.model_name, self.nkod_data_processor, self.language, self.sq_lite, self.graph_db)
        sparql_query = delete_sparql_backticks(sparql_query)
        uris = [dir_name_from_uri(distribution["dataset_uri"]) for distribution in self.matched_lst_dict]

        try:
            error, query_result = self.graph_db.query_sparql_graphdb(sparql_query, uris)

            if error is None:
                return NkodShaclResponse(sparql_query=sparql_query, query_result=query_result, is_executable=True)
            else:
                return self.error_loop(error, sparql_query)

        except Exception as e:
                return self.error_loop(str(e), sparql_query)
    
    def error_loop(self, error: str, failing_query: str) -> NkodShaclResponse:
        nkod_shacl = NkodShacl()

        for i in range(self.nkod_data_processor.NKOD_ERROR_LOOP_RETRIES):
            sparql_query = nkod_shacl.generate_sparql_query_error(self.query, self.matched_lst_dict, self.llm_provider,
                                                            self.model_name, self.nkod_data_processor, self.language,
                                                            self.sq_lite, self.graph_db, error, failing_query)
            sparql_query = delete_sparql_backticks(sparql_query)
            uris = [dir_name_from_uri(distribution["dataset_uri"]) for distribution in self.matched_lst_dict]

            try:
                error, query_result = self.graph_db.query_sparql_graphdb(sparql_query, uris)
                if error is None:
                    return NkodShaclResponse(sparql_query=sparql_query, query_result=query_result, is_executable=True)
                else:
                    failing_query = sparql_query
                    continue
            except Exception as e:
                failing_query = sparql_query
                error = str(e)

        return NkodShaclResponse(sparql_query=failing_query, query_result=["ERROR, please reformat your query"], is_executable=False)

    def parse_query_result(self):
        pass
