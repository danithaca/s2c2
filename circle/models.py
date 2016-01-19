import random
import string
from collections import defaultdict
from enum import Enum

from account.models import SignupCode
from django.core.urlresolvers import reverse

from django.db import models
from django.conf import settings
from p2.utils import UserRole, TrustLevel, TrustedMixin


class Circle(TrustedMixin, models.Model):
    """
    Define the circles users could join.
    """

    class Type(Enum):
        PERSONAL = 1
        PUBLIC = 2
        # AGENCY = 3          # obsolete in favor of "PUBLIC" with options
        # SUPERSET = 4        # obsolete in favor of CircleTag (not implemented)
        # SUBSCRIBER = 5    # people who suscribed to certain circles
        # LOOP = 6          # the circle of people who added me as favorite.
        # PARENT = 7          # obsolete in p2/v5
        # SITTER = 8          # obsolete in p2/v5

        # PUBLIC vs. TAG: tag membership is approved by default. flat hierarchy.
        # TAG = 9             # tag-like circle type in v3 design. obsolete in p2/v5. using "PUBLIC" with options
        # HELPER = 10       # the circle that tracks the helpers (members) to circle-owner. e.g, daniel helped tyler, and daniel is in tyler's helper list.
        # HYBRID = 11       # both as parent and as sitter

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    homepage = models.URLField(max_length=200, blank=True)

    config = models.TextField(blank=True, help_text='JSON field for special settings.')
    # possible settings:
    # - whether to allow parents/sitters join themselves
    # - whether membership requires approval (for either admins or the members)
    # - whether the circle should be listed in the directory
    # - whether to hide parents and/or sitters in group membership display (e.g., UM family helpers should only show sitters, not parents)

    type = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in Type])

    # the last resort to access someone in the circle. usually we'll use membership.
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # "active" is obsolete. need to remove at some point.
    active = models.BooleanField(default=True)
    mark_agency = models.BooleanField(default=False, help_text='Whether this circle is "Agency". Only valid for public circles.')
    # use this name to be distinguished from Membership.approved.
    mark_approved = models.NullBooleanField(default=None, help_text='Whether this circle is approved by site admins. Only valid for public circles.')

    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership')

    # circle's listing area. doesn't necessarily mean every member in the circle have to be in the area
    area = models.ForeignKey('puser.Area')
    signup_code = models.OneToOneField('account.SignupCode', blank=True, null=True, on_delete=models.SET_NULL)

    def to_proxy(self):
        assert isinstance(self, Circle)
        if self.type == Circle.Type.PERSONAL.value and not isinstance(self, PersonalCircle):
            self.__class__ = PersonalCircle
        elif self.type == Circle.Type.PUBLIC.value and not isinstance(self, PublicCircle):
            self.__class__ = PublicCircle
        return self

    def display(self):
        name = self.owner.get_full_name() or self.owner.username
        if self.type == Circle.Type.PERSONAL.value:
            return '%s\'s network' % name
        # elif self.type == Circle.Type.PARENT.value:
        #     return '%s\'s friend' % name
        # elif self.type == Circle.Type.SITTER.value:
        #     return '%s\'s babysitter' % name
        else:
            return self.name

    def __str__(self):
        return self.name

    # @deprecated
    # def add_member(self, user, membership_type=None, approved=None):
    #     """
    #     depreated in favor of "activate_membership"
    #     :return: if membership already exists, return it. otherwise, create the membership with default.
    #     """
    #     defaults = {'active': True}
    #     if membership_type is not None:
    #         defaults['type'] = membership_type
    #     if approved is not None:
    #         defaults['approved'] = approved
    #     membership, created = Membership.objects.update_or_create(member=user, circle=self, defaults=defaults)
    #
    #     # this should not be here. caller should specify the info.
    #     if created and self.is_type_personal():
    #         membership.approved = True
    #         membership.save()
    #
    #     return membership

    # def _activate_membership(self, user, membership_type=None, approved=None):
    #     """
    #     :return: if membership already exists, return it with active set to True. otherwise, create the membership with default.
    #     """
    #     defaults = {'active': True}
    #     if membership_type is not None:
    #         defaults['type'] = membership_type
    #     if approved is not None:
    #         defaults['approved'] = approved
    #     membership, created = Membership.objects.update_or_create(member=user, circle=self, defaults=defaults)
    #     return membership

    # # this structure allows override activate_membership without overriding _active_membership()
    # def activate_membership(self, user, membership_type=None, approved=None):
    #     self._activate_membership(user, membership_type, approved)

    def activate_membership(self, user, **kwargs):
        """
        If membership already exists, set active to True. otherwise, create the membership with default.
        This will regardless create a "membership" object, because "activate" is always the first step to initiate a "Membership" object.
        """
        defaults = {}
        defaults.update(kwargs)
        defaults['active'] = True
        membership, created = Membership.objects.update_or_create(member=user, circle=self, defaults=defaults)

    def deactivate_membership(self, user):
        """
        If membership already exists, set to False. otherwise, do nothing
        """
        try:
            membership = self.get_membership(user)
            if membership.active:
                membership.active = False
                membership.approved = None
                membership.save()
        except Membership.DoesNotExist:
            pass

    def approve_membership(self, user):
        """
        If membership already exists, approve it. otherwise, do nothing
        """
        try:
            membership = self.get_membership(user)
            if not membership.approved:
                membership.approved = True
                membership.save()
        except Membership.DoesNotExist:
            pass

    def disapprove_membership(self, user):
        try:
            membership = self.get_membership(user)
            if not membership.approved is False:
                membership.approved = False
                membership.save()
        except Membership.DoesNotExist:
            pass

    def get_membership(self, user):
        return Membership.objects.get(member=user, circle=self)

    # def get_active_member(self):
    #     return self.members.filter(membership__active=True)

    def is_type_personal(self):
        return self.type == Circle.Type.PERSONAL.value

    def is_type_public(self):
        return self.type == Circle.Type.PUBLIC.value

    # def is_type_parent(self):
    #     return self.type == Circle.Type.PARENT.value
    #
    # def is_type_sitter(self):
    #     return self.type == Circle.Type.SITTER.value

    # def is_type_tag(self):
    #     return self.type == Circle.Type.TAG.value

    def is_agency(self):
        return self.is_type_public() and self.mark_agency

    def count(self, as_role=None):
        qs = self.membership_set.filter(active=True).exclude(approved=False)
        if as_role is not None:
            qs.filter(as_role=as_role)
        return qs.count()

    def is_empty(self):
        return self.count() == 0

    def is_valid_member(self, user):
        try:
            membership = self.get_membership(user)
            if membership.active and membership.approved:
                return True
            else:
                return False
        except Membership.DoesNotExist:
            return False

    def is_membership_activated(self, user):
        try:
            membership = self.get_membership(user)
            if membership.active and membership.approved is not False:
                return True
            else:
                return False
        except Membership.DoesNotExist:
            return False

    def get_absolute_url(self):
        return reverse('circle:group_view', kwargs={'pk': self.id})

    def get_admin_users(self):
        admin_members = set([member for member in self.members.filter(membership__as_admin=True)])
        admin_members.add(self.owner)
        return admin_members

    def is_user_trusted(self, user, level=TrustLevel.COMMON.value):
        proxy = self.to_proxy()
        assert proxy.__class__ != Circle
        return proxy.is_user_trusted(user, level)

    def generate_signup_code(self):
        code_length = 4
        # try a maximum of 1000 times
        for i in range(1000):
            # token = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(code_length))
            # excluding o O l 1.
            token = ''.join(random.SystemRandom().choice('abcdefghijkmnpqrstuvwxyz23456789') for _ in range(code_length))
            if not SignupCode.exists(code=token):
                code = SignupCode.objects.create(code=token)
                self.signup_code = code
                self.save()
                return code
        else:
            raise RuntimeError('Cannot generate a unique token')

    def get_signup_code(self, force=True):
        code = self.signup_code
        if code:
            return code
        elif force:
            code = self.generate_signup_code()
            return code
        else:
            return code


# class PersonalCircleManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(type=Circle.Type.PERSONAL.value)


class PersonalCircle(Circle):
    class Meta:
        proxy = True
    # objects = PersonalCircleManager()

    def display(self):
        name = self.owner.get_full_name() or self.owner.username
        return '%s\'s network' % name

    def activate_membership(self, user, **kwargs):
        as_role = kwargs.get('as_role', UserRole.PARENT.value)
        if as_role == UserRole.PARENT.value:
            # this is parent-parent friendship
            friendship = Friendship(self.owner, user)
            # todo: need to figure out whether to further process kwargs.
            friendship.activate()
        else:
            super().activate_membership(user, **kwargs)

    def approve_membership(self, user):
        # by approving the membership, that means I will want to activate the membership as well.
        try:
            membership = self.get_membership(user)
            if membership.is_valid_parent_relation():
                friendship = Friendship(self.owner, user)
                friendship.approve()
                return
        except Membership.DoesNotExist:
            pass
        super().approve_membership(user)

    def disapprove_membership(self, user):
        try:
            membership = self.get_membership(user)
            if membership.is_valid_parent_relation():
                friendship = Friendship(self.owner, user)
                friendship.disapprove()
                return
        except Membership.DoesNotExist:
            pass
        super().approve_membership(user)

    def deactivate_membership(self, user):
        try:
            membership = self.get_membership(user)
            if membership.as_role == UserRole.PARENT.value:
                friendship = Friendship(self.owner, user)
                friendship.deactivate()
                return
        except Membership.DoesNotExist:
            pass
        super().deactivate_membership(user)

    def is_user_trusted(self, user, level=TrustLevel.COMMON.value):
        # delegate 'trust" to the personal circle's owner
        return self.owner.to_puser().is_user_trusted(user, level)


class PublicCircle(Circle):
    class Meta:
        proxy = True

    def is_user_trusted(self, user, level=TrustLevel.COMMON.value):
        trust_level = TrustLevel.NONE.value
        # FULL level: group owner
        if self.owner == user:
            trust_level = TrustLevel.FULL.value
        # CLOSE level: group admins
        elif user in self.get_admin_users():
            trust_level = TrustLevel.CLOSE.value
        # COMMON level: active/approved member
        elif self.is_valid_member(user):
            trust_level = TrustLevel.COMMON.value
        else:
            try:
                membership = self.get_membership(user)
                if membership.approved is False:
                    trust_level = TrustLevel.FORBIDDEN.value
                else:
                    trust_level = TrustLevel.REMOTE.value
            except:
                pass
        # REMOTE level: pending approval members
        return trust_level >= level


# class ParentCircleManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(type=Circle.Type.PARENT.value)


# TODO: make obsolete in favor of "Membership" activate/deactivate.
# class ParentCircle(Circle):
#     # proxy circle for "Parent" type
#     class Meta:
#         proxy = True
#
#     objects = ParentCircleManager()
#
#     # case 1: no membership exists. after execution, both membership active and approved.
#     # case 2: A->B not active, B->A active but not approved: B->A should be approved
#     # case 3: A->B not active, B-> not active not approved: B->A active and approved.
#     # simply put, when activating parent membership, the other person will activate everything as well.
#     # this doesn't allow "decline friendship request", but we could change the behavior later
#     # if by default adding a friend needs approval, we'll set "approved" to be False by default, and then have the other person approve before activate.
#     def activate_membership(self, user, membership_type=None, approved=None):
#         # first, active this membership, and set approved to be True regardless of the paramenter.
#         self._activate_membership(user, membership_type, True)
#         # since the parent-parent relationship should be symmetric, we should active the other membership, if not already.
#         other_circle = user.to_puser().my_circle(type=Circle.Type.PARENT, area=self.area)
#         assert isinstance(other_circle, ParentCircle)
#         other_circle._activate_membership(self.owner, membership_type, True)
#
#     def deactivate_membership(self, user):
#         # first, deactivate the membership
#         super().deactivate_membership(user)
#         # then set "approved" as False to the other membership.
#         other_circle = user.to_puser().my_circle(type=Circle.Type.PARENT, area=self.area)
#         try:
#             other_membership = other_circle.get_membership(self.owner)
#             if other_membership.approved:
#                 other_membership.approved = False
#                 other_membership.save()
#         except Membership.DoesNotExist:
#             pass


# class SupersetRel(models.Model):
#     """
#     Many-many to track circle inclusions.
#     """
#
#     # child can be any type of circle
#     child = models.ForeignKey(Circle, related_name='child')
#     # parent has to be 'superset'
#     parent = models.ForeignKey(Circle, related_name='parent', limit_choices_to={'type': Circle.Type.SUPERSET.value})
#
#     created = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         unique_together = ('child', 'parent')


class Membership(models.Model):
    """
    User-Circle membership.
    For a membership, there is an "initiator" who initiate the membership (personal: owners; public: members).
    There is an "target" who would review the membership and either prove or disapprove (personal: members; public: owners and admins)
    The 'active' field is for the "initiator". The "approved" field is for the "target"
    """

    member = models.ForeignKey(settings.AUTH_USER_MODEL)
    circle = models.ForeignKey(Circle)

    as_role = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in (UserRole.PARENT, UserRole.SITTER)], default=UserRole.PARENT.value)
    as_admin = models.BooleanField(default=False)
    #as_parent = models.BooleanField(default=True)
    #as_sitter = models.BooleanField(default=False)

    # the next few columns are only used in personal circle, to specify the relationship between circle owner and the member.
    rel_direct_family = models.BooleanField(default=False)          # parents and grandparents of the kids
    rel_extended_family = models.BooleanField(default=False)        # uncles, aunts, cousins
    rel_neighbor = models.BooleanField(default=False)               # live close together
    rel_colleague = models.BooleanField(default=False)              # work together
    rel_friend = models.BooleanField(default=False)                 # share friendship
    rel_kid_friend = models.BooleanField(default=False)             # the kids are friends (kids go to school together)
    # rel_other = models.CharField(max_length=100, blank=True)        # other relationship. might not show.

    # this specifies whether the user is disabled or activated
    # private circle (favorite): whether the member is still in the circle
    # public circle: whether the member wants to be in the circle, or resigned.
    active = models.BooleanField(default=False)

    # whether the membership is approved by authorities or a panel.
    # private circle: should always be true, because private list are always approved by the owner. if the member doesn't want to be included, it could be set as false.
    # public circle: someone (either the owner or a panel) needs to approve the membership.
    # agency: usually should always be true. subscribers are always true.
    approved = models.NullBooleanField(blank=True, null=True, default=None)

    # seems we don't need a "owner" type. the admin will suffice
    # type = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in Type], default=Type.NORMAL.value)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # allow the member or circle owner add note to the membership
    note = models.TextField(blank=True)

    class Meta:
        # here we assume a user won't have multiple "membership" instances to the same circle.
        # relieving the assumption will affect many existing code
        unique_together = ('member', 'circle')

    # def is_type_normal(self):
    #     return self.type == Membership.Type.NORMAL.value

    # def is_type_partial(self):
    #     return self.type == Membership.Type.PARTIAL.value

    def is_admin(self):
        return self.member == self.circle.owner or self.as_admin

    def is_joined(self):
        # this helps determine whether to show "Join" or not in group admin
        return self.active and self.approved is not False

    def __str__(self):
        return '%s (%s)' % (self.member.get_name(), self.circle.display())

    def is_active(self):
        return self.active

    def is_disapproved(self):
        return self.approved is False

    def is_pending_approval(self):
        return self.approved is None

    def is_star(self):
        # return self.is_admin() or self.type == Membership.Type.FAVORITE.value
        # todo: might need more logic here
        return self.is_admin()

    # def deactivate(self):
    #     # todo: code dedup for Circle->deactivate_membership
    #     if self.active is True:
    #         # make 'active' as False regardless
    #         self.active = False
    #         self.save()
    #         # this is is a parent in a personal circle. then, do the mutual relation
    #         if self.type == Circle.Type.PARENT.value and self.as_parent:
    #             other_circle = self.member.to_puser().my_circle(type=Circle.Type.PERSONAL, area=self.area)
    #
    #         other_membership = Membership.objects.filter(member=self.circle.owner, circle__owner=)
    #
    #     try:
    #         other_membership = other_circle.get_membership(self.owner)
    #         if other_membership.approved:
    #             other_membership.approved = False
    #             other_membership.save()
    #     except Membership.DoesNotExist:
    #         pass

    def is_valid_parent_relation(self, validate_initial_user=None, validate_target_user=None):
        if validate_initial_user is not None and validate_initial_user != self.circle.owner:
            return False
        if validate_target_user is not None and validate_target_user != self.member:
            return False
        return self.circle.type == Circle.Type.PERSONAL.value and self.as_role == UserRole.PARENT.value

    def is_valid_sitter_relation(self, validate_initial_user=None, validate_target_user=None):
        if validate_initial_user is not None and validate_initial_user != self.circle.owner:
            return False
        if validate_target_user is not None and validate_target_user != self.member:
            return False
        return self.circle.type == Circle.Type.PERSONAL.value and self.as_role == UserRole.SITTER.value

    def is_valid_group_membership(self, validate_circle=None, validate_target_user=None):
        if validate_circle is not None and validate_circle != self.circle:
            return False
        if validate_target_user is not None and validate_target_user != self.member:
            return False
        return self.circle.type == Circle.Type.PUBLIC.value

    def is_role_parent(self):
        return self.as_role == UserRole.PARENT.value

    def is_role_sitter(self):
        return self.as_role == UserRole.SITTER.value

    def deactivate(self):
        # since a membership object is unique to a member in a circle, we'll just delegate it to the circle. or is it???
        circle = self.circle.to_proxy()
        circle.deactivate_membership(self.member)
        self.refresh_from_db()
        assert self.active is False

    def js_display_role(self):
        return UserRole(self.as_role).name.lower()

    # def js_display_circle_type(self):
    #     return Circle.Type(self.circle.type).name.lower()

    def get_circle(self):
        circle = self.circle
        circle.user_membership = self
        return circle


class UserConnection(object):
    """
    This is about how two users are connected. Similar things are in Match. Might need to combine in the future.
    """
    def __init__(self, initiate_user, target_user, membership_list=[]):
        self.initiate_user = initiate_user.to_puser()
        self.target_user = target_user.to_puser()
        self.membership_list = membership_list       # this is the membership list that has "target_user" as members.

        self.star = False       # make whether the target user should have a "star"
        self.note = ''          # which note to show about the target_user.

    def add_membership(self, membership):
        # we cannot assume membership.member is equal to self.target_user.
        # self.membership_list is just a list of memberships that are relevant to the initiate_user => target_user UserConnection
        # how to use the membership_list is up to the application.

        # assert membership.member == self.target_user
        assert membership is not None and isinstance(membership, Membership)
        self.membership_list.append(membership)

    def update_membership_list(self, new_membership_list):
        existing = set(self.membership_list)
        for membership in new_membership_list:
            if membership not in existing:
                self.add_membership(membership)

    def get_circle_list(self):
        circle_count = defaultdict(int)
        for membership in self.membership_list:
            circle_count[membership.circle] += 1
        circle_list = [(k, v) for k, v in circle_count.items()]
        circle_sorted_by_count = [t[0] for t in sorted(circle_list, key=lambda l: l[1], reverse=True)]
        return circle_sorted_by_count

    def get_circle_list_public_only(self):
        circles = self.get_circle_list()
        return [c for c in circles if c.type == Circle.Type.PUBLIC.value]

    def to_reverse(self):
        # this doesn't use all the other properties (eg membership_list)
        return UserConnection(self.target_user, self.initiate_user)

    def trusted(self, level=TrustLevel.COMMON.value):
        if isinstance(level, TrustLevel):
            level = level.value
        return self.trust_level() >= level

    # note: trust level is asymmetric
    # this is whether and how much the "initiate" user trust the "target" user.
    def trust_level(self):
        # Trust one's self is FULL
        if self.initiate_user == self.target_user:
            return TrustLevel.FULL.value

        # level is COMMON: someone in my personal circles, regardless of whether they are parents or babysitters.
        my_personal_circles = Circle.objects.filter(type=Circle.Type.PERSONAL.value, owner=self.initiate_user)
        target_memberships = Membership.objects.filter(circle__in=my_personal_circles, member=self.target_user, active=True)
        if target_memberships.filter(as_admin=True).exists():
            return TrustLevel.CLOSE.value
        elif target_memberships.exists():
            return TrustLevel.COMMON.value

        # COMMON: someone i'm part of her personal circle which I approved
        their_personal_circles = Circle.objects.filter(type=Circle.Type.PERSONAL.value, owner=self.target_user)
        if Membership.objects.filter(circle__in=their_personal_circles, member=self.initiate_user, approved=True).exists():
            return TrustLevel.COMMON.value

        from contract.models import Match, Contract

        # COMMON: anyone who has a "match" object within +/1 7days window
        # window_start = timezone.now() - timedelta(days=7)
        # window_end = timezone.now() + timedelta(days=7)
        # if Match.objects.filter(target_user=self.initiate_user, contract__initiate_user=self.target_user, contract__event_end__lt=window_end, contract__event_start__gt=window_start).exists():
        #     return TrustLevel.COMMON.value
        # if Match.objects.filter(target_user=self.target_user, contract__initiate_user=self.initiate_user, contract__event_end__lt=window_end, contract__event_start__gt=window_start).exists():
        #     return TrustLevel.COMMON.value

        # CLOSE: trust anyone who have a confirmed match regardless of time
        if Contract.objects.filter(initiate_user=self.initiate_user, confirmed_match__target_user=self.target_user, status__in=(Contract.Status.CONFIRMED.value, Contract.Status.SUCCESSFUL.value)).exists():
            return TrustLevel.CLOSE.value
        if Contract.objects.filter(initiate_user=self.target_user, confirmed_match__target_user=self.initiate_user, status__in=(Contract.Status.CONFIRMED.value, Contract.Status.SUCCESSFUL.value)).exists():
            return TrustLevel.CLOSE.value

        # REMOTE: friend's friends, sitters in extended network.
        personal_circle_membership = self.initiate_user.personal_circle_membership_queryset().filter(active=True, approved=True).values_list('member__id', flat=True)
        my_network_circles = Circle.objects.filter(type=Circle.Type.PERSONAL.value, owner__id__in=personal_circle_membership)
        if Membership.objects.filter(circle__in=my_network_circles, active=True, member=self.target_user).exclude(approved=False).exists():
            return TrustLevel.REMOTE.value

        # REMOTE: trust someone in the public/TAG circles where I'm a member of.
        my_public_circles = Circle.objects.filter(type=Circle.Type.PUBLIC.value, membership__member=self.initiate_user, membership__active=True).exclude(membership__approved=False)
        if Membership.objects.filter(circle__in=my_public_circles, member=self.target_user, active=True).exclude(approved=False).exists():
            return TrustLevel.REMOTE.value

        return TrustLevel.NONE.value

    # could raise DoesNotExist or multiple find.
    def find_personal_membership(self, area=None):
        if area is None:
            area = self.initiate_user.get_area()
        return Membership.objects.get(member=self.target_user, circle__type=Circle.Type.PERSONAL.value, circle__owner=self.initiate_user, circle__area=area)

    # shared connection: in my parents friends' network
    def find_shared_connection_personal(self):
        # find all the parents in my network, regardless of area
        my_parent_membership = Membership.objects.filter(circle__owner=self.initiate_user, circle__type=Circle.Type.PERSONAL.value, active=True, as_role=UserRole.PARENT.value).exclude(approved=False)
        my_parent_list = set([m.member for m in my_parent_membership])
        # find membership of the target_user in those parents' network. we don't use "as_role" here, which results in both parents and sitters.
        result_membership = Membership.objects.filter(member=self.target_user, circle__owner__in=my_parent_list, circle__type=Circle.Type.PERSONAL.value, active=True).exclude(approved=False)
        return list(result_membership)

    # compared to "find_shared_connection_personal", this only works for parents-parent, not for parents-sitter
    # also, this returns the list of PUsers, not membership.
    def find_shared_connection_personal_symmetric(self):
        my_list = Membership.objects.filter(circle__owner=self.initiate_user, circle__type=Circle.Type.PERSONAL.value, active=True).exclude(approved=False).values_list('member__id', flat=True)
        your_list = Membership.objects.filter(circle__owner=self.target_user, circle__type=Circle.Type.PERSONAL.value, active=True).exclude(approved=False).values_list('member__id', flat=True)
        shared_list = set(my_list).intersection(set(your_list))
        from puser.models import PUser
        return list(PUser.objects.filter(pk__in=shared_list))

    # shared connection: both you and i are in the save public circle.
    def find_shared_connection_public(self):
        # my public circle membership
        my_public_membership = Membership.objects.filter(circle__type=Circle.Type.PUBLIC.value, member=self.initiate_user, active=True).exclude(approved=False)
        my_public_circles = set([m.circle for m in my_public_membership])
        # find membership from target user in those public circles
        result_membership = Membership.objects.filter(member=self.target_user, circle__in=my_public_circles, active=True).exclude(approved=False)
        return list(result_membership)

    def find_shared_connection_all(self):
        connection_list = []
        try:
            direct = self.find_personal_membership()
            connection_list.append(direct)
        except (Membership.DoesNotExist, Membership.MultipleObjectsReturned) as e:
            pass
        connection_list.extend(self.find_shared_connection_personal())
        connection_list.extend(self.find_shared_connection_public())
        return connection_list

    def count_served(self):
        from puser.models import PUser
        return PUser.from_user(self.target_user).count_served(self.initiate_user)

    def count_served_reverse(self):
        from puser.models import PUser
        return PUser.from_user(self.initiate_user).count_served(self.target_user)

    def count_served_total(self):
        return self.count_served() + self.count_served_reverse()

    def count_favors(self):
        """
        Return the number of favors the server (match.target_user) has done to the client (contract.initiate_user)
        """
        from puser.models import PUser
        return PUser.from_user(self.target_user).count_favors(self.initiate_user)

    def count_favors_reverse(self):
        from puser.models import PUser
        return PUser.from_user(self.initiate_user).count_favors(self.target_user)

    def count_favors_karma(self):
        """
        Positive number; client owes server favors; negative number: server owes client favor.
        """
        favors = self.count_favors()
        favors_reverse = self.count_favors_reverse()
        return favors - favors_reverse


class Friendship(UserConnection):
    '''
    This is a special type of UserConnection with implied parent-parent friendship in the network.
    '''
    def __init__(self, initiate_user, target_user, main_membership=None, reverse_membership=None):
        super().__init__(initiate_user, target_user)

        # handle main membership
        if main_membership is not None:
            assert main_membership.is_valid_parent_relation(self.initiate_user, self.target_user)
        else:
            try:
                main_membership = self.find_personal_membership()
                # this is tested in is_established()
                # assert main_membership.as_parent is True
            except Membership.DoesNotExist:
                pass

        self.main_membership = main_membership
        if self.main_membership is not None:
            self.add_membership(self.main_membership)

        # handle reverse membership
        if reverse_membership is not None:
            assert reverse_membership.is_valid_parent_relation(self.target_user, self.initiate_user)
        else:
            try:
                reverse_user_connection = UserConnection(self.target_user, self.initiate_user)
                reverse_membership = reverse_user_connection.find_personal_membership(area=self.initiate_user.get_area())
                # assert reverse_membership.as_parent is True
            except Membership.DoesNotExist:
                pass

        self.reverse_membership = reverse_membership
        if self.reverse_membership is not None:
            self.add_membership(self.reverse_membership)

    def to_reverse(self):
        return Friendship(self.target_user, self.initiate_user, self.reverse_membership, self.main_membership)

    def is_established(self):
        return self.main_membership is not None and self.main_membership.active and self.main_membership.approved and self.main_membership.as_role == UserRole.PARENT.value and self.reverse_membership is not None and self.reverse_membership.active and self.reverse_membership.approved and self.reverse_membership.as_role == UserRole.PARENT.value

    def is_pending_approval(self):
        return self.main_membership is not None and self.main_membership.active and self.main_membership.approved is None and self.main_membership.as_role == UserRole.PARENT.value

    def can_activate(self):
        # the only time that this cannot activate is when the target user has already disapproved the case.
        # if that happens, the target user could add/activate the initiate user instead, which will approve the friendship.
        if self.main_membership is not None and self.main_membership.approved is False:
            return False
        else:
            return True

    # this is when the initiate user deactivate friendship with the target user.
    def deactivate(self):
        if self.main_membership is not None and self.main_membership.active is True:
            self.main_membership.active = False
            self.main_membership.save()
        if self.reverse_membership is not None and self.reverse_membership.approved is not False:
            # this implies that the reverse membership is disapproved.
            self.reverse_membership.approved = False
            self.reverse_membership.save()
        assert not self.is_established()

    def approve(self):
        # this is the target user approve the initiate user
        # we assume "approve" always come after "activate", which means the membership object is already created.
        assert self.main_membership is not None and self.reverse_membership is not None
        if self.main_membership.approved is not True:
            self.main_membership.approved = True
            self.main_membership.save()
        # if target_user approves initiate_user, which means target_user should activate the membership as well.
        if self.reverse_membership.active is not True:
            self.reverse_membership.active = True
            self.reverse_membership.save()

    def disapprove(self):
        # this is the target user disapprove the initiate user
        assert self.main_membership is not None and self.reverse_membership is not None
        if self.main_membership.approved is not False:
            self.main_membership.approved = False
            self.main_membership.save()
        # if target_user approves initiate_user, which means target_user should activate the membership as well.
        if self.reverse_membership.active is not False:
            self.reverse_membership.active = False
            self.reverse_membership.save()

    # we need to send a request to the target user for approval
    def activate(self):
        if not self.is_established() and self.can_activate():
            # first, make main_membership active.
            if self.main_membership is not None:
                self.main_membership.active = True
                self.main_membership.as_role = UserRole.PARENT.value
                self.main_membership.save()
            else:
                my_circle = self.initiate_user.get_personal_circle()
                self.main_membership = Membership.objects.create(circle=my_circle, member=self.target_user, as_role=UserRole.PARENT.value, active=True, approved=None)
                self.add_membership(self.main_membership)
            # next, handle the reverse membership to set approve=True
            if self.reverse_membership is not None:
                self.reverse_membership.approved = True
                self.reverse_membership.as_role = UserRole.PARENT.value
                self.reverse_membership.save()
            else:
                other_circle = self.target_user.get_personal_circle(area=self.initiate_user.get_area())
                self.reverse_membership = Membership.objects.create(circle=other_circle, member=self.initiate_user, as_role=UserRole.PARENT.value, active=False, approved=True)
                self.add_membership(self.reverse_membership)
        # simply activate a membership does not automatically get approved (which is required for "established")
        # assert self.is_established()