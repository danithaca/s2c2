from abc import ABCMeta, abstractmethod


class RecommenderStrategy(ABCMeta):
    """
    Strategy pattern.
    """

    @abstractmethod
    def recommend(self, contract):
        """
        Given the contract, compute and persist the recommended matches and return the "Match" objects.
        """

class RecentFavoriteRecommender(RecommenderStrategy):
    def recommend(self, contract):
        pass