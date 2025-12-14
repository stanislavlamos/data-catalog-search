import json
from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.model_handler import LLMProviderHandler
from src.schemas.nkod_openai_files_request import NkodOpenAiFilesRequest
from src.schemas.nkod_openai_files_response import NkodOpenAiFilesResponse
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_openai_files import NkodOpenAiFiles
from src.utils import delete_sparql_backticks, dir_name_from_uri


class NkodOpenAiFilesPipeline:
    def __init__(self, request: NkodOpenAiFilesRequest):
        self.llm_provider = LLMProviderHandler.get_model(request.provider_name, request.model_name)
        self.query = request.query
        self.matched_lst_dict = request.matched_lst_dict
        self.nkod_data_processor = NkodDataProcessor("nkod")
        self.model_name = request.model_name
        self.graph_db = GraphDb(self.nkod_data_processor.catalog_name)
        self.sq_lite = SqLite(self.nkod_data_processor.metadata_sql_path)
        self.language = request.language

    def run(self) -> NkodOpenAiFilesResponse:
        nkod_openai_files = NkodOpenAiFiles()
        vs_id = self.get_vector_store_id()
        sparql_query, new_vs_id = nkod_openai_files.generate_sparql_query(self.query, self.matched_lst_dict, self.llm_provider, self.model_name, self.nkod_data_processor, self.language, self.sq_lite, self.graph_db, vs_id)
        sparql_query = delete_sparql_backticks(sparql_query)
        uris = [dir_name_from_uri(distribution["dataset_uri"]) for distribution in self.matched_lst_dict]

        try:
            error, query_result = self.graph_db.query_sparql_graphdb(sparql_query, uris)

            if error is None:
                return NkodOpenAiFilesResponse(sparql_query=sparql_query, query_result=query_result, is_executable=True)
            else:
                return self.error_loop(error, sparql_query, new_vs_id)

        except Exception as e:
            return self.error_loop(str(e), sparql_query, new_vs_id)

    def error_loop(self, error: str, failing_query: str, new_vs_id: str) -> NkodOpenAiFilesResponse:
        nkod_openai_files = NkodOpenAiFiles()
        for i in range(self.nkod_data_processor.NKOD_ERROR_LOOP_RETRIES):
            sparql_query, _ = nkod_openai_files.generate_sparql_query_error(self.query, self.matched_lst_dict, self.llm_provider,
                                                                self.model_name, self.nkod_data_processor,
                                                                self.language,
                                                                self.sq_lite, self.graph_db, error, failing_query, new_vs_id)
            sparql_query = delete_sparql_backticks(sparql_query)
            uris = [dir_name_from_uri(distribution["dataset_uri"]) for distribution in self.matched_lst_dict]

            try:
                error, query_result = self.graph_db.query_sparql_graphdb(sparql_query, uris)
                if error is None:
                    return NkodOpenAiFilesResponse(sparql_query=sparql_query, query_result=query_result, is_executable=True)
                else:
                    failing_query = sparql_query
                    continue
            except Exception as e:
                failing_query = sparql_query
                error = str(e)

        return NkodOpenAiFilesResponse(sparql_query=failing_query, query_result=["ERROR, please reformat your query"],
                               is_executable=False)

    def parse_query_result(self):
        pass

    def get_vector_store_id(self) -> str | None:
        if self.matched_lst_dict is None or len(self.matched_lst_dict) > 1:
            return None

        with open(self.nkod_data_processor.vector_stores_json, "r") as f:
            return json.load(f)[dir_name_from_uri(self.matched_lst_dict[0]["dataset_uri"])]
    