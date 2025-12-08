from src.db.graph_db import GraphDb
from src.services.nkod_data_processor import NkodDataProcessor
from src.utils import dir_name_from_uri
import os
from tqdm import tqdm
import pandas as pd
from src.sparql_queries import get_distinct_named_graphs_graphdb
import shutil


class NkodGraphDbUploader:
    def __init__(self, catalog_name: str = "nkod") -> None:
        self.catalog_name = catalog_name
        self.graph_db = GraphDb(catalog_name)
        self.nkod_data_processor = NkodDataProcessor(catalog_name)
    
    def upload_ofn_distributions(self) -> str:
        metadata_df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)

        for dataset_uri in tqdm(metadata_df['dataset_uri'], desc="Uploading OFN distributions to GraphDB"):
            dir_name_uri = dir_name_from_uri(dataset_uri)
            dir_path = os.path.join(self.nkod_data_processor.distribution_download_location, dir_name_uri)
            jsonld_fpath = os.path.join(dir_path, "distribution_expanded.jsonld")
            
            try:
                graph_iri = f"{dir_name_uri}"
                self.graph_db.add_new_namegraph_graphdb_remote(graph_iri, jsonld_fpath, "application/ld+json")
            except Exception as e:
                print(f"⚠️ JSONLD file not found for dataset {dataset_uri} at {jsonld_fpath}. Skipping upload.")
    
        self.align_named_graphs_with_ofn_dataset()

    @staticmethod
    def upload_trig_metadata(catalog_name: str = "nkod") -> str:
        graph_db = GraphDb(catalog_name)
        nkod_data_processor = NkodDataProcessor(catalog_name)
        graph_db.push_trig_to_graphdb_remote(nkod_data_processor.metadata_path, nkod_data_processor.trig_metadata_named_graph_iri)
        print("NKOD TRIG metadata uploaded to GraphDB successfully.")
    
    def align_named_graphs_with_ofn_dataset(self):
        _, data = self.graph_db.query_sparql_graphdb(get_distinct_named_graphs_graphdb)   
        parsed_values = [binding['g']['value'] for binding in data['results']['bindings']]
        parsed_values = [graph_uri.split('/')[-1] for graph_uri in parsed_values]
        metadata_df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)
        dataset_uris_to_remove = []

        for dataset_uri in metadata_df['dataset_uri']:
            dir_name_uri = dir_name_from_uri(dataset_uri)
            
            if dir_name_uri not in parsed_values:
                dataset_uris_to_remove.append(dataset_uri)
                shutil.rmtree(os.path.join(self.nkod_data_processor.distribution_download_location, dir_name_uri))

        metadata_df = metadata_df[~metadata_df['dataset_uri'].isin(dataset_uris_to_remove)]
        metadata_df.to_csv(self.nkod_data_processor.ofn_metadata_csv_path, index=False)
