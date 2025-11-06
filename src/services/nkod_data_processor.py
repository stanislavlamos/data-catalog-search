import requests
import os
import csv
import math
import pandas as pd
from tqdm import tqdm
from ..db.chroma_db import ChromaDb
from ..db.graph_db import GraphDb
from ..db.sq_lite import SqLite
from ..models.base import BaseEmbeddingProvider
from ..schemas.schemas import NkodDistribution
from ..sparql_queries import get_catalogs_metadata_and_themes_nkod_remote, \
    get_all_dcat_themes_nkod_remote, get_dataset_distributions_nkod_remote, get_dataset_publisher_nkod_remote, \
    get_publisher_by_dataset_nkod_remote, get_all_distributions_and_formats_nkod_remote
from src.services.base_data_processor import BaseDataProcessor
from ..sql_queries import get_keywords_czech_nkod, get_keywords_english_nkod, get_descriptions_czech_nkod, \
    get_descriptions_english_nkod, get_titles_english_nkod, get_titles_czech_nkod, get_themes_labels_english_nkod, \
    get_themes_labels_czech_nkod, get_themes_definitions_czech_nkod, get_themes_definitions_english_nkod, \
    get_titles_from_uri_czech_nkod, get_titles_from_uri_english_nkod
from ..utils import split_keywords_sql_output, print_keywords_stats, \
    print_titles_stats, print_descs_stats, prepare_nkod_keywords_for_chromadb, batch_list, \
    split_themes_sql_output, prepare_nkod_themes_properties_for_chromadb, \
    split_descs_sql_output, split_titles_sql_output, prepare_nkod_descs_for_chromadb, prepare_nkod_titles_for_chromadb, intersect_dataframes


class NkodDataProcessor(BaseDataProcessor):

    METADATA_URL = "https://data.gov.cz/soubor/nkod.trig"
    DISTRIBUTIONS_URL = "https://data.gov.cz/soubor/distribuce.csv"
    DATASETS_URL = "https://data.gov.cz/soubor/datové-sady.csv"
    NKOD_ENDPOINT = "https://data.gov.cz/sparql"
    BATCH_SIZE = 40000
    URIS_TO_SKIP = "https://data.gov.cz/zdroj/podněty-na-data-k-otevření/"
    DCAT_THEMES_URL = "http://publications.europa.eu/resource/authority/data-theme"
    NKOD_FILE_FORMAT_PREFIX = "http://publications.europa.eu/resource/authority/file-type/"

    def __init__(self, catalog_name: str, metadata_fname: str = "nkod_metadata.trig", distributions_fname: str = "nkod_distributions.csv", datasets_fname: str = "nkod_datasets.csv"):
        super().__init__(catalog_name, metadata_fname, distributions_fname, datasets_fname)
        
        self.metadata_csv_path = os.path.join(self.data_path, "nkod_metadata.csv")
        self.metadata_sql_table_name = "nkod_metadata"
        self.metadata_sql_path = os.path.join(self.data_path, f"{self.metadata_sql_table_name}.db")
        self.themes_csv_path = os.path.join(self.data_path, "nkod_themes.csv")
        self.themes_sql_table_name = "nkod_themes"
        self.themes_sql_path = os.path.join(self.data_path, f"{self.themes_sql_table_name}.db")
        self.distributions_sql_table_name = "nkod_distributions"
        self.distributions_sql_path = os.path.join(self.data_path, f"{self.distributions_sql_table_name}.db")
        self.distributions_csv_path = os.path.join(self.data_path, "nkod_distributions.csv")
        self.publishers_csv_path = os.path.join(self.data_path, "nkod_publishers.csv")

        self.sql_columns_metadata = [
            "dataset_uri",
            "title_cs",
            "title_en",
            "description_cs",
            "description_en",
            "keywords_cs",
            "keywords_en",
            "themes",
            "has_rdf_distribution"
        ]
        self.sql_columns_themes = [
            "theme_name",
            "theme_label_cz",
            "theme_label_en",
            "theme_definition_cz",
            "theme_definition_en"
        ]
        self.sql_columns_distributions = [
            'datová_sada',
            'distribuce',
            'typ',
            'název',
            'autorskéDílo',
            'databázeAutorskéDílo',
            'zvláštníPrávoPořizovateleDatabáze',
            'osobníÚdaje',
            'přístupovéUrl',
            'formátSouboru',
            'mediaTypeSouboru',
            'odkazNaSchémaSouboru',
            'popisPřístupovéhoBoduSlužby',
            'specifikaceSlužby'
        ]

        self.format_to_extension_distribution = {
            "json-ld": "jsonld",
            "json_ld": "jsonld",
            "rdf_n_triples": "nt",
            "rdf_turtle": "ttl",
            "rdf_n_quads": "nq",
            "rdf_trig": "trig",
            "csv": "csv",
            "zip": "zip",
            "rdf_xml": "rdf",
            "json": "json",
            "xml": "xml"
        }
        self.rdf_file_formats = ['jsonld', 'ttl', 'trig', 'rdf', 'nq', 'nt']

        self.vectordb_path = self.data_path
        self.keywords_collection_name = "nkod_keywords"
        self.descriptions_collection_name = "nkod_descriptions"
        self.titles_collection_name = "nkod_titles"
        self.themes_labels_collection_name = "nkod_themes_labels"
        self.themes_definitions_collection_name = "nkod_themes_definitions"

    def download_catalog_metadata(self) -> None:
        response = requests.get(self.METADATA_URL)
        response.raise_for_status()

        with open(self.metadata_path, "wb") as f:
            f.write(response.content)

        print(f"Metadata file downloaded as {self.metadata_path}")

    def download_catalog_distributions(self) -> None:
        response = requests.get(self.DISTRIBUTIONS_URL)
        response.raise_for_status()

        with open(self.distributions_path, "wb") as f:
            f.write(response.content)

        print(f"Distributions file downloaded as {self.distributions_path}")
    
    def download_catalog_datasets(self):
        response = requests.get(self.DATASETS_URL)
        response.raise_for_status()

        with open(self.datasets_path, "wb") as f:
            f.write(response.content)

        print(f"Datasets file downloaded as {self.distributions_path}")

    def _index_keywords(self, sq_lite: SqLite, embedding_provider: BaseEmbeddingProvider, chroma_db: ChromaDb, language: str = "cs", verbose: bool = False) -> None:
        if language == "cs":
            result = sq_lite.query_data(get_keywords_czech_nkod, {"table_name": self.metadata_sql_table_name})
        else: # language == "en"
            result = sq_lite.query_data(get_keywords_english_nkod, {"table_name": self.metadata_sql_table_name})

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
            result = sq_lite.query_data(get_descriptions_czech_nkod, {"table_name": self.metadata_sql_table_name})
        else: # language == "en"
            result = sq_lite.query_data(get_descriptions_english_nkod, {"table_name": self.metadata_sql_table_name})

        split_sql = split_descs_sql_output(result, f"description_{language}")
        texts, ids, metadatas = prepare_nkod_descs_for_chromadb(split_sql, f"description_{language}")
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
            result = sq_lite.query_data(get_titles_czech_nkod, {"table_name": self.metadata_sql_table_name})
        else:  # language == "en"
            result = sq_lite.query_data(get_titles_english_nkod, {"table_name": self.metadata_sql_table_name})

        split_sql = split_titles_sql_output(result, f"title_{language}")
        texts, ids, metadatas = prepare_nkod_titles_for_chromadb(split_sql, f"title_{language}")
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

    def _index_themes_labels(self, sq_lite: SqLite, embedding_provider: BaseEmbeddingProvider, chroma_db: ChromaDb, language: str = "cs"):
        if language == "cs":
            result = sq_lite.query_data(get_themes_labels_czech_nkod, {"table_name": self.themes_sql_table_name})
        else:  # language == "en"
            result = sq_lite.query_data(get_themes_labels_english_nkod, {"table_name": self.themes_sql_table_name})

        split_sql = split_themes_sql_output(result, f"theme_label_{language}")
        texts, ids, metadatas = prepare_nkod_themes_properties_for_chromadb(split_sql, f"theme_label_{language}")

        chroma_db.flush_cache()
        chroma_db.create_collection(f"{self.themes_labels_collection_name}_{language}", embedding_provider)
        chroma_db.add_documents(texts, ids, metadatas)

    def _index_themes_definitions(self, sq_lite: SqLite, embedding_provider: BaseEmbeddingProvider, chroma_db: ChromaDb, language: str = "cs"):
        if language == "cs":
            result = sq_lite.query_data(get_themes_definitions_czech_nkod, {"table_name": self.themes_sql_table_name})
        else:  # language == "en"
            result = sq_lite.query_data(get_themes_definitions_english_nkod, {"table_name": self.themes_sql_table_name})

        split_sql = split_themes_sql_output(result, f"theme_definition_{language}")
        texts, ids, metadatas = prepare_nkod_themes_properties_for_chromadb(split_sql, f"theme_definition_{language}")

        chroma_db.flush_cache()
        chroma_db.create_collection(f"{self.themes_definitions_collection_name}_{language}", embedding_provider)
        chroma_db.add_documents(texts, ids, metadatas)

    def index_catalog_themes(self, sq_lite: SqLite, embedding_provider: BaseEmbeddingProvider, chroma_db: ChromaDb):
        self._index_themes_labels(sq_lite, embedding_provider, chroma_db)
        self._index_themes_labels(sq_lite, embedding_provider, chroma_db, language="en")
        self._index_themes_definitions(sq_lite, embedding_provider, chroma_db)
        self._index_themes_definitions(sq_lite, embedding_provider, chroma_db, language="en")

    def create_metadata_csv(self, graph_db: GraphDb) -> None:
        sparql_results = graph_db.query_sparql_remote(get_catalogs_metadata_and_themes_nkod_remote, self.NKOD_ENDPOINT)
        table = {}

        for r in sparql_results["results"]["bindings"]:
            ds = r["dataset"]["value"]
            prop = r["prop"]["value"]
            val = r["value"]["value"]
            lang = r.get("lang", {}).get("value", "")

            if self.URIS_TO_SKIP in ds:
                continue

            if ds not in table:
                table[ds] = {
                    "keywords_cs": set(),
                    "keywords_en": set(),
                    "title_cs": set(),
                    "title_en": set(),
                    "desc_cs": set(),
                    "desc_en": set(),
                    "themes": set(),
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

            elif prop == "themes":
                table[ds]["themes"].add(val)

        with open(self.metadata_csv_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.sql_columns_metadata)

            for ds, vals in table.items():
                writer.writerow([
                    ds,
                    ";_; ".join(sorted(vals["title_cs"])),
                    ";_; ".join(sorted(vals["title_en"])),
                    ";_; ".join(sorted(vals["desc_cs"])),
                    ";_; ".join(sorted(vals["desc_en"])),
                    ";_; ".join(sorted(vals["keywords_cs"])),
                    ";_; ".join(sorted(vals["keywords_en"])),
                    ";_; ".join(sorted(vals["themes"])),
                ])

        aligned_metadata_df = self.align_metadata_with_nkod()
        aligned_metadata_df_with_rdf_distribution = self.check_metadata_for_rdf_distributions(graph_db, aligned_metadata_df)
        aligned_metadata_df_with_rdf_distribution.to_csv(self.metadata_csv_path, index=False)
        print(f"Created metadata CSV file at {self.metadata_csv_path}")

    def create_themes_csv(self, graph_db: GraphDb) -> None:
        sparql_results = graph_db.query_sparql_remote(get_all_dcat_themes_nkod_remote, self.NKOD_ENDPOINT)
        csv_columns = self.sql_columns_themes
        table = []

        for row in sparql_results["results"]["bindings"]:
            table.append({
                "theme_name": row.get("themeName", {}).get("value", ""),
                "theme_label_cz": row.get("themeLabelCzStr", {}).get("value", ""),
                "theme_label_en": row.get("themeLabelEnStr", {}).get("value", ""),
                "theme_definition_cz": row.get("themeDefinitionCzStr", {}).get("value", ""),
                "theme_definition_en": row.get("themeDefinitionEnStr", {}).get("value", "")
            })

        with open(self.themes_csv_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            writer.writerows(table)

        print(f"CSV created with themes created at {self.themes_csv_path}")

    def create_metadata_sql(self, sq_lite: SqLite):
        sq_lite.create_table(self.metadata_sql_table_name, self.sql_columns_metadata)
        sq_lite.insert_data_from_csv(self.metadata_sql_table_name, self.metadata_csv_path)

        print(f"Created SQL table '{self.metadata_sql_table_name}' in {self.metadata_sql_path}")

    def create_themes_sql(self, sq_lite: SqLite):
        sq_lite.create_table(self.themes_sql_table_name, self.sql_columns_themes)
        sq_lite.insert_data_from_csv(self.themes_sql_table_name, self.themes_csv_path)

        print(f"Created SQL table '{self.themes_sql_table_name}' in {self.themes_sql_path}")

    def create_distributions_sql(self, sq_lite: SqLite):
        sq_lite.create_table(self.distributions_sql_table_name, self.sql_columns_distributions)
        sq_lite.insert_data_from_csv(self.distributions_sql_table_name, self.distributions_csv_path)

        print(f"Created SQL table '{self.distributions_sql_table_name}' in {self.distributions_sql_path}")

    def get_dataset_distributions(self, dataset_uri: str, graph_db: GraphDb) -> list[NkodDistribution]:
        dataset_uri_with_braces = f"<{dataset_uri}>"
        formated_query = get_dataset_distributions_nkod_remote.format(dataset_uri=dataset_uri_with_braces)
        sparql_results = graph_db.query_sparql_remote(formated_query, self.NKOD_ENDPOINT)
        parsed_results = [NkodDistribution(**{k: v['value'] for k, v in b.items()}) for b in sparql_results['results']['bindings']]

        return parsed_results

    def create_dataset_publisher_csv(self, graph_db: GraphDb):
        # TODO: nefunguje, fixnout
        sparql_results = graph_db.query_sparql_remote(get_dataset_publisher_nkod_remote, self.NKOD_ENDPOINT)
        output_dict = {}

        for item in sparql_results["results"]["bindings"]:
            uri = item['dataset']['value']
            lang = item['lang']['value']
            publisher = item['value']['value']

            if uri not in output_dict:
                output_dict[uri] = {}

            if lang == 'cs':
                output_dict[uri]['publisher_cs'] = publisher
            elif lang == 'en':
                output_dict[uri]['publisher_en'] = publisher

        csv_rows = []
        for uri, publishers in output_dict.items():
            row = {'dataset_uri': uri}
            row.update(publishers)
            csv_rows.append(row)

        fieldnames = ['dataset_uri', 'publisher_cs', 'publisher_en']

        with open(self.publishers_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in csv_rows:
                writer.writerow(row)

        print(f"CSV file '{self.publishers_csv_path}' created successfully.")

    def get_dataset_publisher(self, dataset_uri: str, graph_db: GraphDb, language: str) -> str:
        formated_query = get_publisher_by_dataset_nkod_remote.format(dataset_uri=dataset_uri)
        sparql_results = graph_db.query_sparql_remote(formated_query, self.NKOD_ENDPOINT)

        return sparql_results['results']['bindings'][0][f"name_{language}"]["value"]

    def get_dataset_title(self, dataset_uri, sq_lite: SqLite, language: str) -> str:
        sql_query = get_titles_from_uri_czech_nkod if language == "cs" else get_titles_from_uri_english_nkod
        result = sq_lite.query_data(sql_query, {"dataset_uri": dataset_uri, "table_name": self.metadata_sql_table_name})

        return result[0][0]

    def dataset_uri_has_rdf_distribution(self, dataset_uri: str, distributions_and_formats_df: pd.DataFrame) -> bool:
        dataset_distributions = distributions_and_formats_df[distributions_and_formats_df["dataset_uri"] == dataset_uri]

        for format_uri in dataset_distributions["format"]:
            if format_uri is None:
                continue

            if format_uri.startswith(self.NKOD_FILE_FORMAT_PREFIX):
                format_key = format_uri.replace(self.NKOD_FILE_FORMAT_PREFIX, "")
                file_extension = self.format_to_extension_distribution.get(format_key.lower(), None)
                
                if file_extension in self.rdf_file_formats:
                    return True
        
        return False

    def check_metadata_for_rdf_distributions(self, graph_db: GraphDb, aligned_metadata_df: pd.DataFrame) -> pd.DataFrame:
        distributions_and_formats_df = self.get_all_distributions_and_formats(graph_db)
        aligned_distributions_and_formats_df = intersect_dataframes(distributions_and_formats_df, aligned_metadata_df, left_on="dataset_uri", right_on="dataset_uri") 
        has_rdf_distribution_lst = []
        processed_datasets = []

        for dataset_uri in tqdm(
            aligned_distributions_and_formats_df["dataset_uri"],
            desc="Checking RDF distributions",
            total=len(aligned_distributions_and_formats_df),
            unit="dataset"
        ):
            if dataset_uri not in processed_datasets:
                has_rdf_distribution = self.dataset_uri_has_rdf_distribution(dataset_uri, distributions_and_formats_df)
                has_rdf_distribution_lst.append({
                    "dataset_uri": dataset_uri,
                    "has_rdf_distribution": has_rdf_distribution
                })
                processed_datasets.append(dataset_uri)

        rdf_df = pd.DataFrame(has_rdf_distribution_lst)
        aligned_metadata_df = aligned_metadata_df.merge(rdf_df, on="dataset_uri", how="left")

        return aligned_metadata_df

    def align_metadata_with_nkod(self) -> pd.DataFrame:
        nkod_datasets_df = pd.DataFrame(pd.read_csv(self.datasets_path)["datová_sada"].unique(), columns=["datová_sada"])
        nkod_distributions_df = pd.DataFrame(pd.read_csv(self.distributions_path)["datová_sada"].unique(), columns=["datová_sada"])
        my_metadata_df = pd.read_csv(self.metadata_csv_path)
        aligned_metadata_df = intersect_dataframes(my_metadata_df, nkod_datasets_df, left_on="dataset_uri", right_on="datová_sada")
        aligned_metadata_df = intersect_dataframes(aligned_metadata_df, nkod_distributions_df, left_on="dataset_uri", right_on="datová_sada")
        
        columns_to_drop = ['has_rdf_distribution', 'datová_sada_x', 'datová_sada_y']
        aligned_metadata_df = aligned_metadata_df.drop(columns=columns_to_drop, errors='ignore')

        
        return aligned_metadata_df

    def get_all_distributions_and_formats(self, graph_db: GraphDb) -> pd.DataFrame:
        sparql_results = graph_db.query_sparql_remote(get_all_distributions_and_formats_nkod_remote, self.NKOD_ENDPOINT)

        data = [
            {
                'dataset_uri': binding['dataset']['value'],
                'distribution_uri': binding.get('distribution', {}).get('value', None),
                'format': binding.get('format', {}).get('value', None)
            }
            for binding in sparql_results['results']['bindings']
        ]

        return pd.DataFrame(data)
    