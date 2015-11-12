from collections import defaultdict
from enum import Enum
from django.core.urlresolvers import reverse

from django.db import models
from django.conf import settings
from p2.utils import deprecated, UserRole


class Circle(models.Model):
    """
    Define the circles users could join.
    """

    class Type(Enum):
        PERSONAL = 1
        PUBLIC = 2
        AGENCY = 3          # obsolete in favor of "PUBLIC" with options
        SUPERSET = 4        # obsolete in favor of CircleTag (not implemented)
        # SUBSCRIBER = 5    # people who suscribed to certain circles
        # LOOP = 6          # the circle of people who added me as favorite.
        PARENT = 7          # obsolete in p2/v5
        SITTER = 8          # obsolete in p2/v5

        # PUBLIC vs. TAG: tag membership is approved by default. flat hierarchy.
        TAG = 9             # tag-like circle type in v3 design. obsolete in p2/v5. using "PUBLIC" with options
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
    active = models.BooleanField(default=True)

    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership')

    # circle's listing area. doesn't necessarily mean every member in the circle have to be in the area
    area = models.ForeignKey('puser.Area')

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
        elif self.type == Circle.Type.PARENT.value:
            return '%s\'s friend' % name
        elif self.type == Circle.Type.SITTER.value:
            return '%s\'s babysitter' % name
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

    def get_membership(self, user):
        return Membership.objects.get(member=user, circle=self)

    # def get_active_member(self):
    #     return self.members.filter(membership__active=True)

    def is_type_personal(self):
        return self.type == Circle.Type.PERSONAL.value

    def is_type_public(self):
        return self.type == Circle.Type.PUBLIC.value

    def is_type_parent(self):
        return self.type == Circle.Type.PARENT.value

    def is_type_sitter(self):
        return self.type == Circle.Type.SITTER.value

    def is_type_tag(self):
        return self.type == Circle.Type.TAG.value

    def count(self, membership_type=None):
        qs = self.membership_set.filter(active=True, approved=True)
        if type is not None:
            qs.filter(type=membership_type)
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


class PublicCircle(Circle):
    class Meta:
        proxy = True


class ParentCircleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Circle.Type.PARENT.value)


# TODO: make obsolete in favor of "Membership" activate/deactivate.
class ParentCircle(Circle):
    # proxy circle for "Parent" type
    class Meta:
        proxy = True

    objects = ParentCircleManager()

    # case 1: no membership exists. after execution, both membership active and approved.
    # case 2: A->B not active, B->A active but not approved: B->A should be approved
    # case 3: A->B not active, B-> not active not approved: B->A active and approved.
    # simply put, when activating parent membership, the other person will activate everything as well.
    # this doesn't allow "decline friendship request", but we could change the behavior later
    # if by default adding a friend needs approval, we'll set "approved" to be False by default, and then have the other person approve before activate.
    def activate_membership(self, user, membership_type=None, approved=None):
        # first, active this membership, and set approved to be True regardless of the paramenter.
        self._activate_membership(user, membership_type, True)
        # since the parent-parent relationship should be symmetric, we should active the other membership, if not already.
        other_circle = user.to_puser().my_circle(type=Circle.Type.PARENT, area=self.area)
        assert isinstance(other_circle, ParentCircle)
        other_circle._activate_membership(self.owner, membership_type, True)

    def deactivate_membership(self, user):
        # first, deactivate the membership
        super().deactivate_membership(user)
        # then set "approved" as False to the other membership.
        other_circle = user.to_puser().my_circle(type=Circle.Type.PARENT, area=self.area)
        try:
            other_membership = other_circle.get_membership(self.owner)
            if other_membership.approved:
                other_membership.approved = False
                other_membership.save()
        except Membership.DoesNotExist:
            pass


class SupersetRel(models.Model):
    """
    Many-many to track circle inclusions.
    """

    # child can be any type of circle
    child = models.ForeignKey(Circle, related_name='child')
    # parent has to be 'superset'
    parent = models.ForeignKey(Circle, related_name='parent', limit_choices_to={'type': Circle.Type.SUPERSET.value})

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('child', 'parent')


class Membership(models.Model):
    """
    User-Circle membership.
    For a membership, there is an "initiator" who initiate the membership (personal: owners; public: members).
    There is an "target" who would review the membership and either prove or disapprove (personal: members; public: owners and admins)
    The 'active' field is for the "initiator". The "approved" field is for the "target"
    """

    # obsolete in favor the the booleans
    class Type(Enum):
        NORMAL = 1
        ADMIN = 2
        PARTIAL = 3         # this is a passive membership that only receive notifications, e.g., subscribe to a agency circle
        FAVORITE = 4            # counted as the same user, or sharing the same kids.

    member = models.ForeignKey(settings.AUTH_USER_MODEL)
    circle = models.ForeignKey(Circle)

    as_role = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in (UserRole.PARENT, UserRole.SITTER)], default=UserRole.PARENT.value)
    as_admin = models.BooleanField(default=False)
    #as_parent = models.BooleanField(default=True)
    #as_sitter = models.BooleanField(default=False)

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
    type = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in Type], default=Type.NORMAL.value)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # allow the member or circle owner add note to the membership
    note = models.TextField(blank=True)

    class Meta:
        # here we assume a user won't have multiple "membership" instances to the same circle.
        # relieving the assumption will affect many existing code
        unique_together = ('member', 'circle')

    def is_type_normal(self):
        return self.type == Membership.Type.NORMAL.value

    def is_type_partial(self):
        return self.type == Membership.Type.PARTIAL.value

    def is_admin(self):
        return self.type == Membership.Type.ADMIN.value or self.member == self.circle.owner

    def __str__(self):
        return '%s (%s)' % (self.member.get_name(), self.circle.display())

    def is_disapproved(self):
        return self.approved is False

    def is_pending_approval(self):
        return self.approved is None

    def is_star(self):
        return self.is_admin() or self.type == Membership.Type.FAVORITE.value

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

    def deactivate(self):
        # since a membership object is unique to a member in a circle, we'll just delegate it to the circle. or is it???
        circle = self.circle.to_proxy()
        circle.deactivate_membership(self.member)
        self.refresh_from_db()
        assert self.active is False


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

    def get_circle_list(self):
        circle_count = defaultdict(int)
        for membership in self.membership_list:
            circle_count[membership.circle] += 1
        circle_list = [(k, v) for k, v in circle_count.items()]
        circle_sorted_by_count = [t[0] for t in sorted(circle_list, key=lambda l: l[1], reverse=True)]
        return circle_sorted_by_count

    def to_reverse(self):
        # this doesn't use all the other properties (eg membership_list)
        return UserConnection(self.target_user, self.initiate_user)

    def find_personal_membership(self):
        # could raise DoesNotExist or multiple find.
        area = self.initiate_user.get_area()
        return Membership.objects.get(member=self.target_user, circle__type=Circle.Type.PERSONAL.value, circle__owner=self.initiate_user, circle__area=area)


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
                reverse_membership = reverse_user_connection.find_personal_membership()
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