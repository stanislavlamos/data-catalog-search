from src.services.base_query_matcher import BaseQueryMatcher


class NkodQueryMatcher(BaseQueryMatcher):
    def __init__(self):
        self.matching_keywords = []
        self.matching_descriptions = []
        self.matching_titles = []
        self.matching_distributions = []

    def get_matching_distributions(self):
        pass

    def _get_matching_keywords(self):
        pass

    def _get_matching_descriptions(self):
        pass

    def _get_matching_titles(self):
        pass

    def _get_time_frame(self):
        pass