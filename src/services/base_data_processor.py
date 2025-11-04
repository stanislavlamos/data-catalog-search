from abc import ABC, abstractmethod
import os
from pathlib import Path


class BaseDataProcessor(ABC):
    """Abstract base class for data processors"""

    DATA_DIR = "data"

    def __init__(self, catalog_name: str, metadata_fname: str, distributions_fname: str, datasets_fname: str):
        self.catalog_name = catalog_name
        self.metadata_fname = metadata_fname

        project_dir = Path(__file__).resolve().parent.parent.parent
        self.data_path = os.path.join(project_dir, self.DATA_DIR, self.catalog_name)
        self.metadata_path = os.path.join(self.data_path, self.metadata_fname)
        self.distributions_path = os.path.join(self.data_path, distributions_fname)
        self.datasets_path = os.path.join(self.data_path, datasets_fname)

    @abstractmethod
    def download_catalog_metadata(self) -> None:
        """Download catalog metadata"""
        pass