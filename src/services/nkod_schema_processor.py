import os.path
from pathlib import Path
from src.schemas.schemas import NkodDistribution
import requests
from urllib.parse import urljoin
import ssl
import json


ssl._create_default_https_context = ssl._create_unverified_context

class NkodSChemaProcessor:

    MAX_RECURSION_DEPTH = 1 # or 3
    DATA_DIR = "data"
    NKOD_FILE_FORMAT_PREFIX = "http://publications.europa.eu/resource/authority/file-type/"

    def __init__(self, catalog_name: str = "nkod"):
        self.catalog_name = catalog_name
        project_dir = Path(__file__).resolve().parent.parent.parent
        self.data_path = os.path.join(project_dir, self.DATA_DIR, self.catalog_name)
        self.tmp_folder_path = os.path.join(self.data_path, "tmp")
        self.rdfizer_config_fname = None
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
        self.nonrdf_file_formats_schema = ['csv', 'json', 'xml']
        # TODO: what about XML files (are they RDF???)?
        self.rdf_file_formats = ['jsonld', 'ttl', 'trig', 'rdf', 'nq', 'nt']
        self.schema_and_distribution_preference = {
            "ttl": 0,
            "rdf": 1,
            "jsonld": 2,
            "trig": 3,
            "nq": 4, # TODO: probrat
            "nt": 5 # TODO: probrat
        }

    def process_schemas(self, lst_of_list_of_distributions: list[list[NkodDistribution]]) -> tuple[list[list[tuple[str, str]]], list[NkodDistribution]]:
        processed_schemas_all = []
        selected_distributions = []

        for list_of_distributions in lst_of_list_of_distributions:
            only_files_distributions = self.filter_only_files(list_of_distributions)
            our_distribution = self.select_best_distribution(only_files_distributions)
            selected_distributions.append(our_distribution)
            schema_format = self.get_schema_format(our_distribution.conformsTo)

            if schema_format is not None:
                if schema_format == "jsonld":
                    combined_schema = self.resolve_json_refs(our_distribution.conformsTo)
                    processed_schemas_all.append([(schema_format, json.dumps(combined_schema, ensure_ascii=False, indent=2))])

                elif schema_format in self.rdf_file_formats:
                    processed_schemas_all.append([(schema_format, requests.get(our_distribution.conformsTo).text)])

                elif schema_format == "zip":
                    raise NotImplementedError

                else: # schema_format in self.nonrdf_file_formats_schema
                    schema_data = None

                    if schema_format == "json":
                        schema_data = self.resolve_json_refs(our_distribution.conformsTo)
                    else:
                        schema_data = requests.get(our_distribution.conformsTo).text

                    processed_schemas_all.append([(schema_format, schema_data)])

            else: # schema_format is None
                raise NotImplementedError
                #processed_schemas.append((schema_format, requests.get(our_schema.conformsTo).text))

        return processed_schemas_all, selected_distributions

    def select_best_distribution(self, distributions: list[NkodDistribution]) -> NkodDistribution:
        def score(distribution: NkodDistribution) -> int:
            sort_score = self.schema_and_distribution_preference.get(self.format_to_extension_distribution.get(distribution.format.replace(self.NKOD_FILE_FORMAT_PREFIX, "").lower(), "Unknown format"), 1000)

            if distribution.conformsTo is None:
                sort_score += 10

            return sort_score

        return sorted(distributions, key=score)[0]

    def process_zip_file(self):
        raise NotImplementedError

    def filter_only_files(self, distributions: list[NkodDistribution]) -> list[NkodDistribution]:
        # TODO: pozdeji pridat do sqlite tabulky
        filtered_distributions = []

        for distribution in distributions:
            if distribution.format is None or distribution.downloadURL is None:
                continue

            elif not self.is_distribution_file(distribution):
                continue

            filtered_distributions.append(distribution)

        return filtered_distributions

    def resolve_json_refs(self, url, visited=None, depth=0):
        if visited is None:
            visited = set()

        if depth > self.MAX_RECURSION_DEPTH:
            return {"$ref": url}

        if url in visited:
            return {"$ref": url}
        visited.add(url)

        try:
            resp = requests.get(url)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            data = {"$ref": url}

        def _resolve(obj, base_url):
            if isinstance(obj, dict):
                if "$ref" in obj and isinstance(obj["$ref"], str):
                    ref_url = urljoin(base_url, obj["$ref"])
                    return self.resolve_json_refs(ref_url, visited, depth + 1)
                else:
                    return {k: _resolve(v, base_url) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_resolve(item, base_url) for item in obj]
            else:
                return obj

        return _resolve(data, url)

    def get_schema_format(self, url: str | None) -> str | None:
        if url is None:
            return None

        return url.rsplit('.', 1)[-1].replace(".", "").lower()

    def is_distribution_file(self, distribution: NkodDistribution) -> bool:
        if distribution.format.startswith(self.NKOD_FILE_FORMAT_PREFIX):
            format_key = distribution.format.replace(self.NKOD_FILE_FORMAT_PREFIX, "")
            file_extension = self.format_to_extension_distribution.get(format_key.lower(), None)
            return file_extension is not None

        return False

    def generate_shacl(self):
        # Generating SHACL shapes from https://shacl-play.sparna.fr/play/generate
        raise NotImplementedError
