import pandas as pd
from src.db.graph_db import GraphDb
from src.services.nkod_data_processor import NkodDataProcessor
from src.utils import dir_name_from_uri
from tqdm import tqdm
from src.sparql_queries import get_relationships_nkod_local, get_classes_nkod_local
import json
import os


class PropertyGenerator:
    def __init__(self, catalog_name: str = "nkod"):
        self.nkod_data_processor = NkodDataProcessor(catalog_name)
        self.graphdb = GraphDb(catalog_name)
    
    def generate_properties(self):
        df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)

        for dataset_uri in tqdm(df["dataset_uri"], desc="Generating properties"):
            dir_name = dir_name_from_uri(dataset_uri)
            classes = self.generate_classes(dir_name)
            relationships = self.generate_relationships(dir_name)

            if relationships is None or classes is None:
                print(f"Not working for URI {dataset_uri}")
                continue

            classes_str = ', '.join(classes)
            relationships_str = ', '.join(relationships)

            with open(f"{os.path.join(self.nkod_data_processor.distribution_download_location, dir_name, "properties.json")}", "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "classes": classes_str,
                        "relationships": relationships_str
                    }, 
                    f,
                    ensure_ascii=False, 
                    indent=2
                )

    def generate_classes(self, dir_name: str) -> str | None:
        sparql_res = self.graphdb.query_sparql_graphdb(get_classes_nkod_local, [dir_name])[1]

        if sparql_res is None:
            return None

        return self.format(sparql_res, "cls")
        

    def generate_relationships(self, dir_name: str) -> str | None:
        sparql_res = self.graphdb.query_sparql_graphdb(get_relationships_nkod_local, [dir_name])[1]

        if sparql_res is None:
            return None

        return self.format(sparql_res, "rel")

    def get_local_name(self, iri: str) -> str:
        if "#" in iri:
            return iri.split("#")[-1]
        elif "/" in iri:
            return iri.split("/")[-1]
        else:
            raise ValueError(f"Unexpected IRI '{iri}', contains neither '#' nor '/'.")

    def format_value(self, iri: str, com: str | None) -> str:
        return f"<{iri}> ({self.get_local_name(iri)}, {com})"


    def format(self, response: dict, key: str) -> list[str]:
        results = []
        
        for row in response.get("results", {}).get("bindings", []):
            cls_value = row[key]["value"]
            com_value = row.get("com", {}).get("value")  # may be missing
            formatted = self.format_value(cls_value, com_value)
            results.append(formatted)
        
        return results

