from abc import ABC
from src.utils import to_lower, strip_text


class BaseQueryMatcher(ABC):

    DATA_DIR = "data"

    def __init__(self, query: str):
        self.query = strip_text(to_lower(query))