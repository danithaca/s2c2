from abc import ABCMeta, abstractmethod
from circle.models import Membership, Circle
from contract.models import Match
from puser.models import PUser


class RecommenderStrategy(metaclass=ABCMeta):
    """
    Strategy pattern.
    """

    @abstractmethod
    def recommend(self, contract):
        """
        Given the contract, compute and persist the recommended matches and return the "Match" objects.
        """

class RandomFavoriteRecommender(RecommenderStrategy):
    def recommend(self, contract):
        initiate_user = PUser.from_user(contract.initiate_user)
        initiate_user_circle = initiate_user.get_personal_circle()
        # order by random and limit by 10.
        for ms in Membership.objects.filter(circle=initiate_user_circle, active=True, approved=True, type=Circle.Type.PERSONAL.value).order_by('?')[:10]:
            target_user = ms.member
            score = ms.updated.timestamp()
            match, created = Match.objects.get_or_create(contract=contract, target_user=target_user, defaults={
                'status': Match.Status.INITIALIZED.value,
                'score': score,
            })

            # we'll not update existing matches
            if not created:
                pass

            # save explanation
            # if initiate_user_circle not in match.circles:
            #     match.circles.add(initiate_user_circle)

            # adding a second time is ok.
            match.circles.add(initiate_user_circle)


# todo: other algorithms
# 1. favorite plus public circle
# 2. used sitters go first


class L1Recommender(RandomFavoriteRecommender):
    """
    The immediate algorithm to run after a new contract to create; should be fast but not thorough.
    """
    pass


class L2Recommender(RandomFavoriteRecommender):
    """
    This runs peoriodically to update contract matches.
    """
    pass
