import pandas as pd
from src.services.nkod_data_processor import NkodDataProcessor
from tqdm import tqdm
import json
from src.utils import dir_name_from_uri
import os


class JsonldToTxt:
    def __init__(self, catalog_name: str = "nkod"):
        self.catalog_name = catalog_name
        self.nkod_data_processor = NkodDataProcessor(self.catalog_name)
    
    def generate(self):
        df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)

        for dataset_uri in tqdm(df["dataset_uri"], desc="Generating txt distribution"):
            dir_name = dir_name_from_uri(dataset_uri)
            
            with open(os.path.join(self.nkod_data_processor.distribution_download_location, dir_name, "distribution_expanded.jsonld"), 'r', encoding='utf-8') as f:
                data = json.load(f)

            data_str = json.dumps(data, indent=2, ensure_ascii=False)
            with open(os.path.join(self.nkod_data_processor.distribution_download_location, dir_name, "distribution_expanded.txt"), 'w', encoding='utf-8') as f:
                f.write(data_str)
