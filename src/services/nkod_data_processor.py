import requests
import os
import csv
from ..db.graph_db import GraphDb
from ..db.sq_lite import SqLite
from ..sparql_queries import get_catalogs_metadata_nkod_remote
from src.services.base_data_processor import BaseDataProcessor


class NkodDataProcessor(BaseDataProcessor):
    """Processor for NKOD data catalog"""

    METADATA_URL = "https://data.gov.cz/soubor/nkod.trig"
    NKOD_ENDPOINT = "https://data.gov.cz/sparql"

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

    def download_catalog_metadata(self) -> None:
        response = requests.get(self.METADATA_URL)
        response.raise_for_status()

        with open(self.metadata_path, "wb") as f:
            f.write(response.content)

        print(f"Metadata file downloaded as {self.metadata_path}")

    def _index_keywords(self, sq_lite: SqLite, language: str = "cs") -> None:
        pass

    def _index_descriptions(self, sq_lite: SqLite, language: str = "cs") -> None:
        pass

    def _index_titles(self, sq_lite: SqLite, language: str = "cs") -> None:
        pass

    def index_catalog_metadata(self, sq_lite: SqLite) -> None:
        self._index_keywords(sq_lite)
        self._index_descriptions(sq_lite)
        self._index_titles(sq_lite)

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
                    "; ".join(sorted(vals["title_cs"])),
                    "; ".join(sorted(vals["title_en"])),
                    "; ".join(sorted(vals["desc_cs"])),
                    "; ".join(sorted(vals["desc_en"])),
                    "; ".join(sorted(vals["keywords_cs"])),
                    "; ".join(sorted(vals["keywords_en"])),
                ])

        print(f"Created metadata CSV file at {self.metadata_csv_path}")

    
    def create_metadata_sql(self, sq_lite: SqLite):
        sq_lite.create_table(self.sql_table_name, self.sql_columns)
        sq_lite.insert_data_from_csv(self.sql_table_name, self.metadata_csv_path)


