from src.db.chroma_db import ChromaDb
from src.db.sq_lite import SqLite
from src.models.openai_provider import OpenAIEmbeddingProvider
from src.services.nkod_data_downloader import NkodDataDownloader
from src.services.nkod_data_processor import NkodDataProcessor
from src.services.nkod_graphdb_uploader import NkodGraphDbUploader
from src.services.shacl_generator import ShaclGenerator


if __name__ == "__main__":
        nkod_data_processor = NkodDataProcessor("nkod")
        sq_lite = SqLite(nkod_data_processor.metadata_sql_path)

        openai_embeddings = OpenAIEmbeddingProvider(model_name="text-embedding-3-large", dimensions=None)
        chroma_db = ChromaDb(nkod_data_processor.vectordb_path)
        nkod_data_processor.index_catalog_metadata(sq_lite, openai_embeddings, chroma_db)
