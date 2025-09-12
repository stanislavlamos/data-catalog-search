from abc import abstractmethod, ABC


class BaseQueryMatcher(ABC):
    @abstractmethod
    def get_matching_distributions(self):
        pass