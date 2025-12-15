from dotenv import load_dotenv
from src.db.chroma_db import ChromaDb
from src.models.openai_provider import OpenAIEmbeddingProvider
from src.models.google_provider import GoogleEmbeddingProvider
from src.services.nkod_data_downloader import NkodDataDownloader
from src.services.nkod_data_processor import NkodDataProcessor
from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite


load_dotenv()

class IndexDataNkod:

    CATALOG_NAME = "nkod"

    def index_data_from_scratch(self) -> None:
        nkod_data_processor = NkodDataProcessor(self.CATALOG_NAME)
        nkod_data_downloader = NkodDataDownloader(nkod_data_processor)
        sq_lite = SqLite(nkod_data_processor.metadata_sql_path)
        self._download_and_preprocess_nkod_metadata(nkod_data_processor, sq_lite, nkod_data_downloader)

    def _download_and_preprocess_nkod_metadata(self, nkod_data_processor: NkodDataProcessor, sq_lite: SqLite, nkod_data_downloader: NkodDataDownloader) -> None:
        graph_db = GraphDb(nkod_data_processor.catalog_name)
        nkod_data_processor.download_catalog_metadata()
        nkod_data_processor.download_catalog_distributions()
        nkod_data_processor.download_catalog_datasets()
        
        nkod_data_processor.create_metadata_csv(graph_db)
        nkod_data_processor.create_themes_csv(graph_db)
        nkod_data_processor.create_dataset_publisher_csv(graph_db)
        nkod_data_processor.enrich_metadata_with_publisher()
        nkod_data_processor.create_ofn_dataset()
        nkod_data_processor.create_distributions_csv(graph_db)
        nkod_data_downloader.download_nkod_data()
    
    def remove_unexpandable_data(self):
        nkod_data_processor = NkodDataProcessor(self.CATALOG_NAME)
        nkod_data_downloader = NkodDataDownloader(nkod_data_processor)
        nkod_data_downloader.remove_unexpandable_data()
    
    def create_sqls(self):
        nkod_data_processor = NkodDataProcessor(self.CATALOG_NAME)
        sq_lite = SqLite(nkod_data_processor.metadata_sql_path)
        nkod_data_processor.create_metadata_sql(sq_lite)
        nkod_data_processor.create_ofn_dataset_sql(sq_lite)
        nkod_data_processor.create_themes_sql(sq_lite)

    def index_nkod_metadata(self):
        nkod_data_processor = NkodDataProcessor(self.CATALOG_NAME)
        sq_lite = SqLite(nkod_data_processor.metadata_sql_path)

        openai_embeddings = GoogleEmbeddingProvider(model_name="gemini-embedding-001", output_dimensionality=None)#OpenAIEmbeddingProvider(model_name="text-embedding-3-large", dimensions=None)
        chroma_db = ChromaDb(nkod_data_processor.vectordb_path)
        nkod_data_processor.index_catalog_themes(sq_lite, openai_embeddings, chroma_db)
        nkod_data_processor.index_catalog_metadata(sq_lite, openai_embeddings, chroma_db)
        print(f"ChromaDB collections: {chroma_db.list_collections()}")
        chroma_db.sizes_of_collections()
