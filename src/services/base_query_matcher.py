from abc import ABC


class BaseQueryMatcher(ABC):

    DATA_DIR = "data"

    def __init__(self, query: str):
        self.query = query