from abc import ABCMeta, abstractmethod
from django.db.models import F
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
        initiate_user_circle = initiate_user.get_personal_circle(contract.area)
        # order by random and limit by 10.
        for ms in Membership.objects.filter(circle=initiate_user_circle, active=True, approved=True, type=Circle.Type.PERSONAL.value).exclude(member=contract.initiate_user).order_by('?')[:10]:
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


# recommend more people till we got every target user
class IncrementalAllRecommender(RecommenderStrategy):
    def recommend(self, contract):
        personal_circle = set(Circle.objects.filter(owner=contract.initiate_user, area=contract.area, type=Circle.Type.PERSONAL.value).values_list('id', flat=True))
        public_circle = set(Circle.objects.filter(membership__member=contract.initiate_user, area=contract.area, type=Circle.Type.PUBLIC.value).values_list('id', flat=True))

        for membership in Membership.objects.filter(circle__in=(personal_circle | public_circle), active=True, approved=True).exclude(member=contract.initiate_user).exclude(member__match__contract=contract, member__match__circles=F('circle')).order_by('?')[:10]:
            target_user = membership.member
            score = membership.updated.timestamp()
            match, created = Match.objects.get_or_create(contract=contract, target_user=target_user, defaults={
                'status': Match.Status.INITIALIZED.value,
                'score': score,
            })
            if not created:
                match.score += score        # increase score if there are more circles.
            match.circles.add(membership.circle)


# todo: other algorithms
# 1. favorite plus public circle
# 2. used sitters go first
# 3. friend's friends.


class L1Recommender(RandomFavoriteRecommender):
    """
    The immediate algorithm to run after a new contract to create; should be fast but not thorough.
    """
    pass


class L2Recommender(IncrementalAllRecommender):
    """
    This runs peoriodically to update contract matches.
    """
    pass
