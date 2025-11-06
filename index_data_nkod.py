from dotenv import load_dotenv
from src.db.chroma_db import ChromaDb
from src.models.openai_provider import OpenAIEmbeddingProvider
from src.services.nkod_data_processor import NkodDataProcessor
from src.db.graph_db import GraphDb
from src.db.sq_lite import SqLite


load_dotenv()

class IndexDataNkod:

    CATALOG_NAME = "nkod"

    def index_data(self) -> None:
        nkod_data_processor = NkodDataProcessor(self.CATALOG_NAME)
        sq_lite = SqLite(nkod_data_processor.metadata_sql_path)
        self._download_and_preprocess_nkod_metadata(nkod_data_processor, sq_lite)
        self._index_nkod_metadata(nkod_data_processor, sq_lite)

    def _download_and_preprocess_nkod_metadata(self, nkod_data_processor: NkodDataProcessor, sq_lite: SqLite) -> None:
        graph_db = GraphDb(nkod_data_processor.catalog_name)
        nkod_data_processor.download_catalog_metadata()
        nkod_data_processor.download_catalog_distributions()
        nkod_data_processor.download_catalog_datasets()
        nkod_data_processor.create_metadata_csv(graph_db)
        nkod_data_processor.create_themes_csv(graph_db)
        nkod_data_processor.create_metadata_sql(sq_lite)
        nkod_data_processor.create_themes_sql(sq_lite)

    def _index_nkod_metadata(self, nkod_data_processor: NkodDataProcessor, sq_lite: SqLite) -> None:
        openai_embeddings = OpenAIEmbeddingProvider(model_name="text-embedding-3-large", dimensions=1536)
        chroma_db = ChromaDb(nkod_data_processor.vectordb_path)
        nkod_data_processor.index_catalog_themes(sq_lite, openai_embeddings, chroma_db)
        nkod_data_processor.index_catalog_metadata(sq_lite, openai_embeddings, chroma_db)
        print(f"ChromaDB collections: {chroma_db.list_collections()}")


if __name__ == "__main__":
    IndexDataNkod().index_data()
