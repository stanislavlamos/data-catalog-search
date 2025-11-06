from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite
from src.models.model_handler import LLMProviderHandler
from src.schemas.nkod_openai_files_request import NkodOpenAiFilesRequest
from src.schemas.nkod_openai_files_response import NkodOpenAiFilesResponse
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_openai_files import NkodOpenAiFiles
from src.utils import delete_sparql_backticks


class NkodOpenAiFilesPipeline:
        def __init__(self, request: NkodOpenAiFilesRequest):
            self.llm_provider = LLMProviderHandler.get_model(request.provider_name, request.model_name)
            self.query = request.query
            self.dataset_uris = request.dataset_uris
            self.nkod_data_processor = NkodDataProcessor("nkod")
            self.model_name = request.model_name
            self.graph_db = GraphDb(self.nkod_data_processor.catalog_name)
            self.sq_lite = SqLite(self.nkod_data_processor.metadata_sql_path)
            self.language = request.language

        def run(self) -> NkodOpenAiFilesResponse:
            nkod_openai_files = NkodOpenAiFiles()
            distributions = [self.nkod_data_processor.get_dataset_distributions(dataset_uri, self.graph_db) for dataset_uri in self.dataset_uris]
            sparql_query, distributions = nkod_openai_files.generate_sparql_query(self.query, distributions, self.llm_provider, self.model_name, self.nkod_data_processor, self.dataset_uris, self.language, self.sq_lite, self.graph_db)
            sparql_query = delete_sparql_backticks(sparql_query)

            #nkod_graph = NkodRdfGraph(distributions)
            query_result = []#nkod_graph.query_graph(sparql_query)

            return NkodOpenAiFilesResponse(sparql_query=sparql_query, query_result=query_result)