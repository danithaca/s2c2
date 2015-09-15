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
        Given the contract, compute and persist the recommended matches.
        """


class RandomFavoriteRecommender(RecommenderStrategy):
    def recommend(self, contract):
        initiate_user = PUser.from_user(contract.initiate_user)
        initiate_user_circle = initiate_user.get_personal_circle(contract.area)
        # order by random and limit by 10.
        for ms in Membership.objects.filter(circle=initiate_user_circle, active=True, approved=True).exclude(member=contract.initiate_user).order_by('?')[:10]:
            target_user = ms.member
            # score = ms.updated.timestamp()
            # IMPORTANT: contract might get changed (status) in "signal" while this is running and lead to "dictionary changed size" error. use id directly.
            try:
                match = Match.objects.get(contract_id=contract.id, target_user=target_user)
            except Match.DoesNotExist:
                match = Match.objects.create(contract_id=contract.id, target_user=target_user, status=Match.Status.INITIALIZED.value, score=1)

            # adding a second time is ok.
            match.circles.add(initiate_user_circle)


# recommend more people till we got every target user
class IncrementalAllRecommender(RecommenderStrategy):
    def _compute_score_from_timestamp(self, timestamp):
        return timestamp / self.contract.event_start.timestamp()

    # return True means a new match is created.
    def _add_match(self, membership):
        contract = self.contract
        target_user = membership.member
        if target_user == contract.initiate_user:
            return False

        score = self._compute_score_from_timestamp(membership.updated.timestamp())
        match, created = Match.objects.get_or_create(contract_id=self.contract.id, target_user=target_user, defaults={
            'status': Match.Status.INITIALIZED.value,
            'score': score,
        })

        if created:
            match.circles.add(membership.circle)
            return True
        else:
            if membership.circle not in match.circles.all():
                match.score += score        # increase score if there are more circles.
                match.save()
                match.circles.add(membership.circle)
            return False

    def recommend(self, contract):
        if not contract.is_active() or contract.is_event_expired():
            return
        self.contract = contract
        client = PUser.from_user(contract.initiate_user)

        ###### handle personal/public circles ########

        personal_circle = set(Circle.objects.filter(owner=contract.initiate_user, area=contract.area, type=Circle.Type.PERSONAL.value).values_list('id', flat=True))
        public_circle = set(Circle.objects.filter(membership__member=contract.initiate_user, area=contract.area, type=Circle.Type.PUBLIC.value, membership__approved=True, membership__active=True).values_list('id', flat=True))
        # for membership in Membership.objects.filter(circle__in=(personal_circle | public_circle), active=True, approved=True).exclude(member=contract.initiate_user).exclude(member__match__contract=contract, member__match__circles=F('circle')).order_by('?')[:10]:
        counter = 0
        for membership in Membership.objects.filter(circle__in=(personal_circle | public_circle), active=True, approved=True).exclude(member=contract.initiate_user).order_by('?'):
            if self._add_match(membership):
                counter += 1
            if counter >= 10:
                break

        ###### handle agency circles #######

        if not contract.is_favor():
            # get the subscriptions of the client
            agency_subscription = set(Circle.objects.filter(membership__member=contract.initiate_user, area=contract.area, membership__type=Membership.Type.PARTIAL.value, membership__active=True).values_list('id', flat=True))
            counter = 0
            # get servers from the agency circles.
            for membership in Membership.objects.filter(circle__type=Circle.Type.AGENCY.value, type=Membership.Type.NORMAL.value, active=True, approved=True, circle__in=agency_subscription).exclude(member=contract.initiate_user).order_by('?'):
                new_match = self._add_match(membership)
                if new_match:
                    counter += 1
                # we only do 5 each time this runs.
                if counter >= 5:
                    break

        ###### handle friend's friend ########

        #personal_list = PUser.objects.filter(membership__circle__in=personal_circle, membership__active=True, membership__approved=True, membership__type=Circle.Type.PERSONAL.value).values_list('id', flat=True)
        # friends' personal circles
        my_personal_circle = client.get_personal_circle()
        my_friends = PUser.objects.filter(membership__circle=my_personal_circle, membership__active=True, membership__approved=True)
        friends_personal_circles = Circle.objects.filter(type=Circle.Type.PERSONAL.value, area=client.get_area(), owner__in=my_friends)
        counter = 0
        for membership in Membership.objects.filter(circle__in=friends_personal_circles, active=True, approved=True).exclude(member=client):
            new_match = self._add_match(membership)
            if new_match:
                counter += 1
                # we only do 5 each time this runs.
            if counter >= 5:
                break


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
