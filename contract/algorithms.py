from abc import ABCMeta, abstractmethod
from itertools import groupby

from circle.models import Membership, Circle
from contract.models import Match, Contract
from puser.models import PUser


class NewRecommenderStrategy(metaclass=ABCMeta):
    def __init__(self, contract):
        self.contract = contract

    def recommend(self):
        pass


################ below is obsolete ###############
# todo: remove later


class RecommenderStrategy(metaclass=ABCMeta):
    """
    Strategy pattern.
    """

    def recommend(self, contract):
        """
        Given the contract, compute and persist the recommended matches.
        """
        if contract.audience_type == Contract.AudienceType.SMART.value:
            count = self.recommend_smart(contract)
        elif contract.audience_type == Contract.AudienceType.CIRCLE.value:
            # recommend circle
            circle_id = contract.parse_audience_data()
            assert circle_id
            circle = Circle.objects.get(pk=circle_id)
            count = self.recommend_circle(contract, circle)
        else:
            count = self.recommend_smart(contract)
        return count

    @abstractmethod
    def recommend_smart(self, contract):
        raise NotImplementedError()

    def recommend_circle(self, contract, circle):
        count = 0
        for membership in circle.membership_set.filter(active=True, approved=True).order_by('?'):
            match_added = self.add_match(contract, membership)
            if match_added:
                count += 1
            if count >= 10:
                break
        return count

    def add_match(self, contract, membership, score=1):
        server = membership.member
        if server == contract.initiate_user:
            return False

        try:
            # IMPORTANT: contract might get changed (status) in "signal" while this is running and lead to "dictionary changed size" error. use id directly.
            match = Match.objects.get(contract_id=contract.id, target_user=server)
            # match exists, only add to circles (and update score)
            if membership.circle not in match.circles.all():
                match.circles.add(membership.circle)
                match.score += score
                match.save()
            return False
        except Match.DoesNotExist:
            match = Match.objects.create(contract_id=contract.id, target_user=server, status=Match.Status.INITIALIZED.value, score=score)
            match.circles.add(membership.circle)
            return True

    def recommend_basic(self, contract):
        client = contract.initiate_user.to_puser()
        if contract.is_favor():
            circle = client.my_circle(Circle.Type.PARENT, contract.area)
        else:
            circle = client.my_circle(Circle.Type.SITTER, contract.area)
        return self.recommend_circle(contract, circle)

    def recommend_sitter_pool(self, contract):
        count = 0
        me = contract.initiate_user.to_puser()
        my_parent_circle = me.my_circle(Circle.Type.PARENT, area=contract.area)
        my_parent_list = my_parent_circle.members.filter(membership__active=True, membership__approved=True).exclude(membership__member=me)
        other_parent_sitter_circle_list = Circle.objects.filter(owner__in=my_parent_list, type=Circle.Type.SITTER.value, area=my_parent_circle.area)
        sitter_membership_pool = Membership.objects.filter(active=True, approved=True, circle__in=other_parent_sitter_circle_list).exclude(member=me).order_by('?')
        for membership in sitter_membership_pool:
            match_added = self.add_match(contract, membership)
            if match_added:
                count += 1
            if count >= 10:
                break
        return count


# todo: other algorithms
# 1. favorite plus public circle
# 2. used sitters go first
# 3. friend's friends.


class L1Recommender(RecommenderStrategy):
    """
    The immediate algorithm to run after a new contract to create; should be fast but not thorough.
    """
    def recommend_smart(self, contract):
        count = self.recommend_basic(contract)
        if count <= 0 and not contract.is_favor():
            count = self.recommend_sitter_pool(contract)
        return count


class L2Recommender(RecommenderStrategy):
    """
    This runs peoriodically to update contract matches.
    """

    def recommend_smart(self, contract):
        if not contract.is_active() or contract.is_event_expired():
            return
        client = contract.get_client()

        # first, run L1 recommender.
        count = self.recommend_basic(contract)

        # next, if it's not a favor, add friends' friends
        if not contract.is_favor():
            count += self.recommend_sitter_pool(contract)
        else:
            # or, if it's a favor, take "family" member's social network
            my_parent_circle = client.my_circle(Circle.Type.PARENT, contract.area)
            family_membership = Membership.objects.filter(circle=my_parent_circle, active=True, approved=True, type=Membership.Type.FAVORITE.value)
            for m in family_membership:
                count += self.recommend_circle(contract, m.member.to_puser().my_circle(Circle.Type.PARENT))

        # next, recommend other parents in my network to take paid job
        if count == 0:
            circle = client.my_circle(Circle.Type.PARENT, contract.area)
            count += self.recommend_circle(contract, circle)

        return count


        # ###### handle personal/public circles ########
        #
        # personal_circle = set(Circle.objects.filter(owner=contract.initiate_user, area=contract.area, type=Circle.Type.PERSONAL.value).values_list('id', flat=True))
        # public_circle = set(Circle.objects.filter(membership__member=contract.initiate_user, area=contract.area, type=Circle.Type.PUBLIC.value, membership__approved=True, membership__active=True).values_list('id', flat=True))
        # # for membership in Membership.objects.filter(circle__in=(personal_circle | public_circle), active=True, approved=True).exclude(member=contract.initiate_user).exclude(member__match__contract=contract, member__match__circles=F('circle')).order_by('?')[:10]:
        # counter = 0
        # for membership in Membership.objects.filter(circle__in=(personal_circle | public_circle), active=True, approved=True).exclude(member=contract.initiate_user).order_by('?'):
        #     if self.add_match(contract, membership):
        #         counter += 1
        #     if counter >= 10:
        #         break
        #
        # ###### handle agency circles #######
        #
        # if not contract.is_favor():
        #     # get the subscriptions of the client
        #     agency_subscription = set(Circle.objects.filter(membership__member=contract.initiate_user, area=contract.area, membership__type=Membership.Type.PARTIAL.value, membership__active=True).values_list('id', flat=True))
        #     counter = 0
        #     # get servers from the agency circles.
        #     for membership in Membership.objects.filter(circle__type=Circle.Type.AGENCY.value, type=Membership.Type.NORMAL.value, active=True, approved=True, circle__in=agency_subscription).exclude(member=contract.initiate_user).order_by('?'):
        #         new_match = self.add_match(contract, membership)
        #         if new_match:
        #             counter += 1
        #         # we only do 5 each time this runs.
        #         if counter >= 5:
        #             break
        #
        # ###### handle friend's friend ########
        #
        # #personal_list = PUser.objects.filter(membership__circle__in=personal_circle, membership__active=True, membership__approved=True, membership__type=Circle.Type.PERSONAL.value).values_list('id', flat=True)
        # # friends' personal circles
        # my_personal_circle = client.get_personal_circle()
        # my_friends = PUser.objects.filter(membership__circle=my_personal_circle, membership__active=True, membership__approved=True)
        # friends_personal_circles = Circle.objects.filter(type=Circle.Type.PERSONAL.value, area=client.get_area(), owner__in=my_friends)
        # counter = 0
        # for membership in Membership.objects.filter(circle__in=friends_personal_circles, active=True, approved=True).exclude(member=client):
        #     new_match = self.add_match(contract, membership)
        #     if new_match:
        #         counter += 1
        #         # we only do 5 each time this runs.
        #     if counter >= 5:
        #         break