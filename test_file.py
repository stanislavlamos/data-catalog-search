from src.services.nkod_data_downloader import NkodDataDownloader
from src.services.nkod_data_processor import NkodDataProcessor


if __name__ == "__main__":
    nkod_data_processor = NkodDataProcessor(catalog_name="nkod")
    nkod_data_downloader = NkodDataDownloader(nkod_data_processor)
    #nkod_data_downloader.download_nkod_data()
    nkod_data_downloader.remove_unexpandable_data()