import os.path
from pathlib import Path
from src.schemas.schemas import NkodDistribution
import requests
from urllib.parse import urljoin
import ssl
import json
import subprocess
from datetime import datetime


ssl._create_default_https_context = ssl._create_unverified_context

class NkodSchemaProcessor:

    MAX_RECURSION_DEPTH = 1 # or 3
    DATA_DIR = "data"
    NKOD_FILE_FORMAT_PREFIX = "http://publications.europa.eu/resource/authority/file-type/"

    def __init__(self, catalog_name: str = "nkod"):
        self.catalog_name = catalog_name
        project_dir = Path(__file__).resolve().parent.parent.parent
        self.data_path = os.path.join(project_dir, self.DATA_DIR, self.catalog_name)
        self.tmp_folder_path = os.path.join(self.data_path, "tmp")
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
        self.rdf_file_formats = ['jsonld', 'ttl', 'trig', 'rdf', 'nq', 'nt']
        self.schema_and_distribution_preference = {
            "ttl": 0,
            "rdf": 1,
            "jsonld": 2,
            "trig": 3,
            "nq": 4, 
            "nt": 5
        }

    def process_schemas(self, distribution: NkodDistribution, dir_path: str):
        schema_format = self.get_schema_format(distribution.conformsTo)

        if schema_format is not None:
            fname = "schema"

            if schema_format == "jsonld":
                combined_schema = self.resolve_json_refs(distribution.conformsTo)
                schema_data = json.dumps(combined_schema, ensure_ascii=False, indent=2)

            elif schema_format in self.rdf_file_formats:
                schema_data = requests.get(distribution.conformsTo, verify=False, timeout=45).text

            else: # schema_format in self.nonrdf_file_formats_schema
                schema_data = None

                if schema_format == "json":
                    schema_data = self.resolve_json_refs(distribution.conformsTo)
                    schema_data = json.dumps(schema_data, ensure_ascii=False, indent=2)
                else:
                    schema_data = requests.get(distribution.conformsTo, verify=False, timeout=45).text

            
            with open(os.path.join(dir_path, f"{fname}.{schema_format}"), 'w', encoding='utf-8') as f:
                f.write(schema_data)

    def resolve_json_refs(self, url, visited=None, depth=0):
        if visited is None:
            visited = set()

        if depth > self.MAX_RECURSION_DEPTH:
            return {"$ref": url}

        if url in visited:
            return {"$ref": url}
        visited.add(url)

        try:
            resp = requests.get(url, verify=False, timeout=45)
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

    def generate_shacl(self, distribution: NkodDistribution, dir_path: str):
        distribution_format = self.get_distribution_format(distribution)
        input_fpath = os.path.join(dir_path, f"distribution.{distribution_format}")
        output_fpath = os.path.join(dir_path, "shacl.ttl")
        
        print("Generating SHACL for:", input_fpath)
        _ = subprocess.run(
            ["shaclgen", input_fpath, "--output", os.path.join(self.tmp_folder_path, output_fpath)],
            check=True,
            capture_output=True,
            text=True
        )
    
    def get_distribution_format(self, distribution: NkodDistribution) -> str | None:
        if distribution.format.startswith(self.NKOD_FILE_FORMAT_PREFIX):
            format_key = distribution.format.replace(self.NKOD_FILE_FORMAT_PREFIX, "")
            file_extension = self.format_to_extension_distribution.get(format_key.lower(), None)
            return file_extension

        return None
