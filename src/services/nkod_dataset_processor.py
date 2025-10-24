from src.schemas.schemas import NkodDistribution


class NkodDatasetProcessor:

    NKOD_FILE_FORMAT_PREFIX = "http://publications.europa.eu/resource/authority/file-type/"

    def __init__(self, catalog_name: str = "nkod"):
        self.catalog_name = catalog_name
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
            "nq": 4,  # TODO: probrat
            "nt": 5  # TODO: probrat
        }

    def process_datasets(self, lst_of_list_of_distributions: list[list[NkodDistribution]]) -> list[NkodDistribution]:
        processed_datasets = []

        for list_of_distributions in lst_of_list_of_distributions:
            only_files_distributions = self.filter_only_files(list_of_distributions)
            our_distribution = self.select_best_distribution(only_files_distributions)

            if self.format_to_extension_distribution.get(our_distribution.format.replace(self.NKOD_FILE_FORMAT_PREFIX, "").lower(), "Unknown format") in self.rdf_file_formats:
                processed_datasets.append(our_distribution)
            else:
                raise NotImplementedError

        return processed_datasets

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

    def select_best_distribution(self, distributions: list[NkodDistribution]) -> NkodDistribution:
        def score(distribution: NkodDistribution) -> int:
            sort_score = self.schema_and_distribution_preference.get(self.format_to_extension_distribution.get(distribution.format.replace(self.NKOD_FILE_FORMAT_PREFIX, "").lower(), "Unknown format"), 1000)

            if distribution.conformsTo is None:
                sort_score += 10

            return sort_score

        return sorted(distributions, key=score)[0]

    def is_distribution_file(self, distribution: NkodDistribution) -> bool:
        if distribution.format.startswith(self.NKOD_FILE_FORMAT_PREFIX):
            format_key = distribution.format.replace(self.NKOD_FILE_FORMAT_PREFIX, "")
            file_extension = self.format_to_extension_distribution.get(format_key.lower(), None)
            return file_extension is not None

        return False
