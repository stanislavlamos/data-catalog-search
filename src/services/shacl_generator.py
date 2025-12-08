import os
import subprocess
import pandas as pd
from tqdm import tqdm
from src.services.nkod_data_processor import NkodDataProcessor
from src.utils import dir_name_from_uri


class ShaclGenerator:
    def __init__(self, catalog_name: str = "nkod"):
        self.nkod_data_processor = NkodDataProcessor(catalog_name)
    
    def generate_shacl(self):
        metadata_df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)

        for dataset_uri in tqdm(metadata_df['dataset_uri'], desc="Generating SHACL files"):
            dir_name_uri = dir_name_from_uri(dataset_uri)
            fname = "distribution_expanded.jsonld"

            try:
                 _ = subprocess.run(
                    ["shaclgen", os.path.join(self.nkod_data_processor.distribution_download_location, dir_name_uri, fname), "--output", os.path.join(self.nkod_data_processor.distribution_download_location, dir_name_uri, "shacl.ttl")],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except Exception as e:
                print(dataset_uri)
                