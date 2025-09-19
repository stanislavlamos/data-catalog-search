import requests
import os
import csv
import math
from ..db.chroma_db import ChromaDb
from ..db.graph_db import GraphDb
from ..db.sq_lite import SqLite
from ..models.base import BaseEmbeddingProvider
from ..sparql_queries import get_catalogs_metadata_nkod_remote
from src.services.base_data_processor import BaseDataProcessor
from ..sql_queries import get_keywords_czech_nkod, get_keywords_english_nkod, get_descriptions_czech_nkod, get_descriptions_english_nkod, get_titles_english_nkod, get_titles_czech_nkod
from ..utils import split_keywords_sql_output, print_keywords_stats, split_descs_or_titles_sql_output, \
    print_titles_stats, print_descs_stats, prepare_nkod_keywords_for_chromadb, batch_list, \
    prepare_nkod_titles_and_descs_for_chromadb


class NkodDataProcessor(BaseDataProcessor):
    """Processor for NKOD data catalog"""

    METADATA_URL = "https://data.gov.cz/soubor/nkod.trig"
    NKOD_ENDPOINT = "https://data.gov.cz/sparql"
    BATCH_SIZE = 40000

    def __init__(self, catalog_name: str, metadata_fname: str = "nkod_metadata.trig"):
        super().__init__(catalog_name, metadata_fname)
        
        self.metadata_csv_path = os.path.join(self.data_path, "nkod_metadata.csv")
        self.sql_table_name = "nkod_metadata"
        self.metadata_sql_path = os.path.join(self.data_path, f"{self.sql_table_name}.db")
        self.sql_columns = [
            "dataset_uri",
            "title_cs",
            "title_en",
            "description_cs",
            "description_en",
            "keywords_cs",
            "keywords_en"
        ]

        self.vectordb_path = self.data_path
        self.keywords_collection_name = "nkod_keywords"
        self.descriptions_collection_name = "nkod_descriptions"
        self.titles_collection_name = "nkod_titles"

    def download_catalog_metadata(self) -> None:
        response = requests.get(self.METADATA_URL)
        response.raise_for_status()

        with open(self.metadata_path, "wb") as f:
            f.write(response.content)

        print(f"Metadata file downloaded as {self.metadata_path}")

    def _index_keywords(self, sq_lite: SqLite, embedding_provider: BaseEmbeddingProvider, chroma_db: ChromaDb, language: str = "cs", verbose: bool = False) -> None:
        if language == "cs":
            result = sq_lite.query_data(get_keywords_czech_nkod, {"table_name": self.sql_table_name})
        else: # language == "en"
            result = sq_lite.query_data(get_keywords_english_nkod, {"table_name": self.sql_table_name})

        split_sql = split_keywords_sql_output(result, f"keywords_{language}")
        texts, ids, metadatas = prepare_nkod_keywords_for_chromadb(split_sql, f"keywords_{language}")
        num_batches = math.ceil(len(texts) / self.BATCH_SIZE)
        batched_texts = batch_list(texts, self.BATCH_SIZE)
        batched_ids = batch_list(ids, self.BATCH_SIZE)
        batched_metadatas = batch_list(metadatas, self.BATCH_SIZE)

        chroma_db.flush_cache()
        chroma_db.create_collection(f"{self.keywords_collection_name}_{language}", embedding_provider)
        chroma_db.add_documents_batched(batched_texts, batched_ids, batched_metadatas, f"keywords_{language}", num_batches)

        if verbose:
            print_keywords_stats(split_sql, f"keywords_{language}", language)

    def _index_descriptions(self, sq_lite: SqLite, embedding_provider: BaseEmbeddingProvider, chroma_db: ChromaDb, language: str = "cs", verbose: bool = False) -> None:
        if language == "cs":
            result = sq_lite.query_data(get_descriptions_czech_nkod, {"table_name": self.sql_table_name})
        else: # language == "en"
            result = sq_lite.query_data(get_descriptions_english_nkod, {"table_name": self.sql_table_name})

        split_sql = split_descs_or_titles_sql_output(result, f"description_{language}")
        texts, ids, metadatas = prepare_nkod_titles_and_descs_for_chromadb(split_sql, f"description_{language}")
        num_batches = math.ceil(len(texts) / self.BATCH_SIZE)
        batched_texts = batch_list(texts, self.BATCH_SIZE)
        batched_ids = batch_list(ids, self.BATCH_SIZE)
        batched_metadatas = batch_list(metadatas, self.BATCH_SIZE)

        chroma_db.flush_cache()
        chroma_db.create_collection(f"{self.descriptions_collection_name}_{language}", embedding_provider)
        chroma_db.add_documents_batched(batched_texts, batched_ids, batched_metadatas, f"description_{language}", num_batches)

        if verbose:
            print_descs_stats(split_sql, f"description_{language}", language)

    def _index_titles(self, sq_lite: SqLite, embedding_provider: BaseEmbeddingProvider, chroma_db: ChromaDb, language: str = "cs", verbose: bool = False) -> None:
        if language == "cs":
            result = sq_lite.query_data(get_titles_czech_nkod, {"table_name": self.sql_table_name})
        else:  # language == "en"
            result = sq_lite.query_data(get_titles_english_nkod, {"table_name": self.sql_table_name})

        split_sql = split_descs_or_titles_sql_output(result, f"title_{language}")
        texts, ids, metadatas = prepare_nkod_titles_and_descs_for_chromadb(split_sql, f"title_{language}")
        num_batches = math.ceil(len(texts) / self.BATCH_SIZE)
        batched_texts = batch_list(texts, self.BATCH_SIZE)
        batched_ids = batch_list(ids, self.BATCH_SIZE)
        batched_metadatas = batch_list(metadatas, self.BATCH_SIZE)

        chroma_db.flush_cache()
        chroma_db.create_collection(f"{self.titles_collection_name}_{language}", embedding_provider)
        chroma_db.add_documents_batched(batched_texts, batched_ids, batched_metadatas, f"title_{language}", num_batches)

        if verbose:
            print_titles_stats(split_sql, f"title_{language}", language)

    def index_catalog_metadata(self, sq_lite: SqLite, embedding_provider: BaseEmbeddingProvider, chroma_db: ChromaDb, verbose: bool = False) -> None:
        self._index_keywords(sq_lite, embedding_provider, chroma_db ,verbose=verbose)
        self._index_keywords(sq_lite, embedding_provider, chroma_db, language="en", verbose=verbose)
        self._index_descriptions(sq_lite, embedding_provider, chroma_db, verbose=verbose)
        self._index_descriptions(sq_lite, embedding_provider, chroma_db, language="en", verbose=verbose)
        self._index_titles(sq_lite, embedding_provider, chroma_db, verbose=verbose)
        self._index_titles(sq_lite, embedding_provider, chroma_db, language="en", verbose=verbose)

    def create_metadata_csv(self, graph_db: GraphDb) -> None:
        sparql_results = graph_db.query_sparql_remote(get_catalogs_metadata_nkod_remote, self.NKOD_ENDPOINT)
        table = {}
        
        for r in sparql_results["results"]["bindings"]:
            ds = r["dataset"]["value"]
            prop = r["prop"]["value"]
            val = r["value"]["value"]
            lang = r.get("lang", {}).get("value", "")

            if ds not in table:
                table[ds] = {
                    "keywords_cs": set(),
                    "keywords_en": set(),
                    "title_cs": set(),
                    "title_en": set(),
                    "desc_cs": set(),
                    "desc_en": set(),
                }

            if prop == "keyword":
                if lang == "cs":
                    table[ds]["keywords_cs"].add(val)
                elif lang == "en":
                    table[ds]["keywords_en"].add(val)

            elif prop == "title":
                if lang == "cs":
                    table[ds]["title_cs"].add(val)
                elif lang == "en":
                    table[ds]["title_en"].add(val)

            elif prop == "description":
                if lang == "cs":
                    table[ds]["desc_cs"].add(val)
                elif lang == "en":
                    table[ds]["desc_en"].add(val)

        with open(self.metadata_csv_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.sql_columns)

            for ds, vals in table.items():
                writer.writerow([
                    ds,
                    ";_; ".join(sorted(vals["title_cs"])),
                    ";_; ".join(sorted(vals["title_en"])),
                    ";_; ".join(sorted(vals["desc_cs"])),
                    ";_; ".join(sorted(vals["desc_en"])),
                    ";_; ".join(sorted(vals["keywords_cs"])),
                    ";_; ".join(sorted(vals["keywords_en"])),
                ])

        print(f"Created metadata CSV file at {self.metadata_csv_path}")

    def create_metadata_sql(self, sq_lite: SqLite):
        sq_lite.create_table(self.sql_table_name, self.sql_columns)
        sq_lite.insert_data_from_csv(self.sql_table_name, self.metadata_csv_path)


