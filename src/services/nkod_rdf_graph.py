from src.schemas.schemas import NkodDistribution
from rdflib import Graph, Dataset, URIRef
import requests
import rdflib.plugins.shared.jsonld.context as jsonld_context
import json


class NkodRdfGraph:

    NKOD_FILE_FORMAT_PREFIX = "http://publications.europa.eu/resource/authority/file-type/"
    GRAPH_IRI = "http://example.org"

    def __init__(self, distributions: list[NkodDistribution]):
        self.distribution_format_to_rdf_format = {
            "json-ld": "json-ld",
            "json_ld": "json-ld",
            "rdf_n_triples": "nt",
            "rdf_turtle": "ttl",
            "rdf_n_quads": "nq",
            "rdf_trig": "trig",
            "rdf_xml": "rdf"
        }
        self.graph = self._create_graph(distributions)

    def _create_graph(self, distributions: list[NkodDistribution]) -> Graph | Dataset:
        if len(distributions) == 1:
            return self._create_simple_graph(distributions)
        else:
            return self._create_multi_graph(distributions)

    def _create_simple_graph(self, distributions: list[NkodDistribution]) -> Graph:
        g = Graph()
        graph_format = distributions[0].format.lower().replace(self.NKOD_FILE_FORMAT_PREFIX, "")
        distribution_str = NkodRdfGraph.download_distribution(distributions[0])
        g.parse(data=distribution_str, format=self.distribution_format_to_rdf_format[graph_format])

        return g

    def _create_multi_graph(self, distributions: list[NkodDistribution]) -> Dataset:
        ds = Dataset()

        for idx, distribution in enumerate(distributions):
            identifier = URIRef(f"{self.GRAPH_IRI}/g{idx+1}")
            g = Graph(identifier=identifier)
            distribution_str = NkodRdfGraph.download_distribution(distribution)
            graph_format = distribution.format.lower().replace(self.NKOD_FILE_FORMAT_PREFIX, "")
            g.parse(data=distribution_str, format=self.distribution_format_to_rdf_format[graph_format])
            ds.add_graph(g)

        return ds

    def query_graph(self, query) -> list:
        return list(self.graph.query(query))

    @staticmethod
    def get_graph(distribution: NkodDistribution) -> Graph:
        NKOD_FILE_FORMAT_PREFIX = "http://publications.europa.eu/resource/authority/file-type/"
        distribution_format_to_rdf_format = {
            "json-ld": "json-ld",
            "json_ld": "json-ld",
            "rdf_n_triples": "nt",
            "rdf_turtle": "ttl",
            "rdf_n_quads": "nq",
            "rdf_trig": "trig",
            "rdf_xml": "rdf"
        }

        g = Graph()
        graph_format = distribution.format.lower().replace(NKOD_FILE_FORMAT_PREFIX, "")
        distribution_str = NkodRdfGraph.download_distribution(distribution)
        g.parse(data=distribution_str, format=distribution_format_to_rdf_format[graph_format])

        return g
    
    @staticmethod
    def download_distribution(distribution: NkodDistribution) -> str:
        response = requests.get(distribution.downloadURL)
        response.raise_for_status()
        distribution_format_to_rdf_format = {
            "json-ld": "json-ld",
            "json_ld": "json-ld",
            "rdf_n_triples": "nt",
            "rdf_turtle": "ttl",
            "rdf_n_quads": "nq",
            "rdf_trig": "trig",
            "rdf_xml": "rdf"
        }
        NKOD_FILE_FORMAT_PREFIX = "http://publications.europa.eu/resource/authority/file-type/"

        graph_format = distribution.format.lower().replace(NKOD_FILE_FORMAT_PREFIX, "")
        if distribution_format_to_rdf_format[graph_format] == "json-ld":
            return json.dumps(json.loads(response.text))

        return response.text
