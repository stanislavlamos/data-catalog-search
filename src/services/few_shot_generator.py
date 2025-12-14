from src.models.openai_provider import OpenAILLMProvider
from src.services.nkod_data_processor import NkodDataProcessor
import pandas as pd


class FewShotGenerator:
    def __init__(self, catalog_name: str = "nkod"):
        self.nkod_data_processor = NkodDataProcessor(catalog_name)
        self.openai_provider = OpenAILLMProvider(model_name="gpt-5")
        self.matched_substring = ["sportoviště", "sběrné dvory", "aktuality", "události", "turistické cíle", "úřední deska"]
        self.example_query_datasets = {
            "sportoviště": {
                "dataset_uri": ["https://data.gov.cz/zdroj/datové-sady/44992785/2c965b64a35a5f89a31d83cd62d8e288", "https://data.gov.cz/zdroj/datové-sady/00235938/1355924590"],
                "dirs": ["2c965b64a35a5f89a31d83cd62d8e288", "1355924590"]
            },
            "sběrné dvory": {
                "dataset_uri": ["https://data.gov.cz/zdroj/datové-sady/00246875/1133220027"],
                "dir": ["1133220027"]
            },
            "aktuality": {
                "dataset_uri": ["https://data.gov.cz/zdroj/datové-sady/00253472/1139317508", "https://data.gov.cz/zdroj/datové-sady/00253383/1137956007"],
                "dir": ["1139317508", "1137956007"]
            },
            "události": {
                "dataset_uri": ["https://data.gov.cz/zdroj/datové-sady/00246875/1168825388", "https://data.gov.cz/zdroj/datové-sady/00240702/1425538386"],
                "dir": ["1168825388", "1425538386"]
            },
            "turistické cíle": {
                "dataset_uri": ["https://data.gov.cz/zdroj/datové-sady/00235938/1355924909"],
                "dir": ["1355924909"]
            },
            "úřední deska": {
                "dataset_uri": ["https://data.gov.cz/zdroj/datové-sady/00260428/1016977215", "https://data.gov.cz/zdroj/datové-sady/70890650/996478121"],
                "dir": ["1016977215", "996478121"]
            }
        }

    def generate_few_shots(self):
        df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)
        #print('\n'.join(list(df["matched_substring"].unique())))
        print('\n'.join(list(df[df["matched_substring"] == 'Turistické cíle']["dataset_uri"])))

    def alter_matched_substring_df_column(self):
        df = pd.read_csv(self.nkod_data_processor.ofn_metadata_csv_path)
        match_map = {m: m for m in self.matched_substring}
        match_map["úřední desky"] = "úřední deska"

        def replace_if_in_list(val):
            val_lower = str(val).lower()
            return match_map.get(val_lower, val)

        df["matched_substring"] = df["matched_substring"].apply(replace_if_in_list)
        df.to_csv(self.nkod_data_processor.ofn_metadata_csv_path, index=False)
