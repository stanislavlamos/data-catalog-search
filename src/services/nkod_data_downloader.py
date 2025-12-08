from src.schemas.schemas import NkodDistribution
from src.services.nkod_data_processor import NkodDataProcessor
import pandas as pd
from src.services.nkod_dataset_processor import NkodDatasetProcessor
from src.services.nkod_schema_processor import NkodSchemaProcessor
import os
from tqdm import tqdm
import rdflib
import traceback
from src.utils import dir_name_from_uri, check_dir_status_os
import shutil


class NkodDataDownloader:
    def __init__(self, nkod_data_processor: NkodDataProcessor):
        self.nkod_data_processor = nkod_data_processor
        self.nkod_dataset_processor = NkodDatasetProcessor()
        self.nkod_schema_processor = NkodSchemaProcessor()
    
    def download_nkod_data(self):
        metadata_df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)
        distributions_df = pd.read_csv(self.nkod_data_processor.distributions_csv_path_queried)
        dataset_distributions_dict = {}
        dataset_uris_to_remove = []
        dir_paths = []

        for dataset_uri in tqdm(metadata_df['dataset_uri'], desc="Downloading NKOD datasets"):
            distribution_rows = distributions_df[distributions_df['dataset'] == dataset_uri]
            distribution_list_of_dicts = distribution_rows.to_dict('records')
            dataset_distributions_dict[dataset_uri] = distribution_list_of_dicts
            distribution_obj_lst = self.create_distribution_obj_lst(distribution_list_of_dicts)
            dir_name_uri = dir_name_from_uri(dataset_uri)
            dir_path = os.path.join(self.nkod_data_processor.distribution_download_location, dir_name_uri)
            os.makedirs(dir_path, exist_ok=True)
            dir_paths.append((dir_path, dataset_uri))

            if not distribution_obj_lst:
                continue

            try:
                best_distribution = self.nkod_dataset_processor.process_datasets(distribution_obj_lst, dir_path)
                self.nkod_schema_processor.process_schemas(best_distribution, dir_path)
            except Exception as e:
                    traceback.print_exc()
                    print(e)
            
        for dir_path, dataset_uri in dir_paths:
            if not check_dir_status_os(dir_path):
                os.rmdir(dir_path)
                dataset_uris_to_remove.append(dataset_uri)
        
        self.remove_unreachable_data(dataset_uris_to_remove)
    
    def create_distribution_obj_lst(self, distribution_rows: list[dict]) -> list[NkodDistribution]:
        obj_lst = []
        
        for row in distribution_rows:
            try:
                distribution = NkodDistribution(
                    dataset_uri=row.get('dataset'),
                    distribution=row.get('distribution'),
                    format=row.get('format'),
                    downloadURL=row.get('downloadURL'),
                    accessURL=row.get('accessURL'),
                    conformsTo=row.get('conformsTo', None) if isinstance(row.get('conformsTo', None), str) else None
                )
                obj_lst.append(distribution)
            except Exception as e:
                continue
        
        return obj_lst
    
    def check_rdflib_parsebility(self, file_path: str) -> bool:
        g = rdflib.Graph()
        try:
            g.parse(file_path)
            return True
        except Exception as e:
            return False
    
    def remove_unreachable_data(self, dataset_uris_to_remove: list[str]):
        if not dataset_uris_to_remove:
            return
        
        metadata_df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)
        metadata_df = metadata_df[~metadata_df['dataset_uri'].isin(dataset_uris_to_remove)]
        metadata_df.to_csv(self.nkod_data_processor.ofn_metadata_csv_path, index=False)
    
    def remove_unexpandable_data(self, fpath: str = "./failed_files_log.txt"):
        extracted_paths = []
        metadata_df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)
        
        with open(fpath, 'r') as f:
            for line in f:
                clean_line = line.strip()
                
                if clean_line:
                    directory_path = os.path.dirname(clean_line)
                    shutil.rmtree(directory_path)
                    extracted_paths.append(directory_path)
                    cur_dir_name = directory_path.split('/')[-1]
                    metadata_df = metadata_df[metadata_df['dataset_uri'].apply(dir_name_from_uri) != cur_dir_name]
        
        metadata_df.to_csv(self.nkod_data_processor.ofn_metadata_csv_path, index=False)
        os.remove(fpath)
        return extracted_paths
       