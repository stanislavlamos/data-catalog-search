from src.schemas.schemas import NkodDistribution
from rdflib import Graph, Dataset, URIRef


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
        g.parse(distributions[0].downloadURL, format=self.distribution_format_to_rdf_format[graph_format])

        return g

    def _create_multi_graph(self, distributions: list[NkodDistribution]) -> Dataset:
        ds = Dataset()

        for idx, distribution in enumerate(distributions):
            identifier = URIRef(f"{self.GRAPH_IRI}/g{idx+1}")
            g = Graph(identifier=identifier)
            graph_format = distribution.format.lower().replace(self.NKOD_FILE_FORMAT_PREFIX, "")
            g.parse(distribution.downloadURL, format=self.distribution_format_to_rdf_format[graph_format])
            ds.add_graph(g)

        return ds

    def query_graph(self, query) -> list:
        print(f"Executing SPARQL query:\n{query}\n")
        print(self.graph)
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
        print(distribution.downloadURL)
        g.parse(distribution.downloadURL, format=distribution_format_to_rdf_format[graph_format])

        return g
