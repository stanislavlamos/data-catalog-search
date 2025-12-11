from src.db.sq_lite import SqLite
from src.services import nkod_data_processor
from src.services.nkod_data_processor import NkodDataProcessor
from src.sql_queries import get_all_datasets_nkod
from src.schemas.all_datasets_response import AllDatasetsResponse


class AllDatasetsPipeline:
    def __init__(self):
        self.nkod_data_processor = NkodDataProcessor("nkod")
        self.sq_lite = SqLite(self.nkod_data_processor.metadata_sql_path)

    def run(self) -> AllDatasetsResponse:
        all_datasets = self._fetch_all_datasets()
        return AllDatasetsResponse(all_datasets=all_datasets)

    def _fetch_all_datasets(self) -> list[dict]:
        sql_response = self.sq_lite.query_data(get_all_datasets_nkod, {"table_name": self.nkod_data_processor.ofn_dataset_sql_table_name})
        datasets = self.parse_sql_response(sql_response)

        return datasets
    
    def parse_sql_response(self, sql_response: list[tuple[str, str, str]]) -> list[dict]:
        datasets = []

        for dataset_uri,title_cs,title_en,description_cs,description_en,keywords_cs,keywords_en,themes,has_rdf_distribution,publisher_en,publisher_cs,matched_substring in sql_response:
            dataset = {
                "dataset_uri": dataset_uri,
                "title_cs": title_cs,
                "title_en": title_en,
                "description_cs": description_cs,
                "description_en": description_en,
                "keywords_cs": keywords_cs,
                "keywords_en": keywords_en,
                "themes": themes,
                "has_rdf_distribution": has_rdf_distribution,
                "publisher_en": publisher_en,
                "publisher_cs": publisher_cs,
                "matched_substring": matched_substring
            }
            datasets.append(dataset)
        
        return datasets
        