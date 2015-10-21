from collections import defaultdict
from enum import Enum
from django.core.urlresolvers import reverse

from django.db import models
from django.conf import settings
from p2.utils import deprecated


class Circle(models.Model):
    """
    Define the circles users could join.
    """

    class Type(Enum):
        PERSONAL = 1        # obsolete in favor of parent/babysitter.
        PUBLIC = 2          # obsolete in favor of tag
        AGENCY = 3
        SUPERSET = 4
        # SUBSCRIBER = 5    # people who suscribed to certain circles
        # LOOP = 6          # the circle of people who added me as favorite.
        PARENT = 7          # parents network in v3 design
        SITTER = 8          # babysitter list in v3 design
        # PUBLIC vs. TAG: tag membership is approved by default. flat hierarchy.
        TAG = 9             # tag-like circle type in v3 design.
        # HELPER = 10       # the circle that tracks the helpers (members) to circle-owner. e.g, daniel helped tyler, and daniel is in tyler's helper list.

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    homepage = models.URLField(max_length=200, blank=True)

    type = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in Type])

    # the last resort to access someone in the circle. usually we'll use membership.
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner')
    created = models.DateTimeField(auto_now_add=True)

    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership')

    # circle's listing area. doesn't necessarily mean every member in the circle have to be in the area
    area = models.ForeignKey('puser.Area')

    def display(self):
        name = self.owner.get_full_name() or self.owner.username
        if self.type == Circle.Type.PERSONAL.value:
            return '%s\'s list' % name
        elif self.type == Circle.Type.PARENT.value:
            return '%s\'s connection' % name
        elif self.type == Circle.Type.SITTER.value:
            return '%s\'s babysitter' % name
        else:
            return self.name

    def __str__(self):
        return self.name

    @deprecated
    def add_member(self, user, membership_type=None, approved=None):
        """
        depreated in favor of "activate_membership"
        :return: if membership already exists, return it. otherwise, create the membership with default.
        """
        defaults = {'active': True}
        if membership_type is not None:
            defaults['type'] = membership_type
        if approved is not None:
            defaults['approved'] = approved
        membership, created = Membership.objects.update_or_create(member=user, circle=self, defaults=defaults)

        # this should not be here. caller should specify the info.
        if created and self.is_type_personal():
            membership.approved = True
            membership.save()

        return membership

    def _activate_membership(self, user, membership_type=None, approved=None):
        """
        :return: if membership already exists, return it with active set to True. otherwise, create the membership with default.
        """
        defaults = {'active': True}
        if membership_type is not None:
            defaults['type'] = membership_type
        if approved is not None:
            defaults['approved'] = approved
        membership, created = Membership.objects.update_or_create(member=user, circle=self, defaults=defaults)
        return membership

    # this structure allows override activate_membership without overriding _active_membership()
    def activate_membership(self, user, membership_type=None, approved=None):
        self._activate_membership(user, membership_type, approved)

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

    def get_membership(self, user):
        return Membership.objects.get(member=user, circle=self)

    def get_active_member(self):
        return self.members.filter(membership__active=True)

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

    def get_absolute_url(self):
        return reverse('circle:tag_view', kwargs={'pk': self.id})


class ParentCircleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Circle.Type.PARENT.value)


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

    class Type(Enum):
        NORMAL = 1
        ADMIN = 2
        PARTIAL = 3         # this is a passive membership that only receive notifications, e.g., subscribe to a agency circle
        FAVORITE = 4            # counted as the same user, or sharing the same kids.

    member = models.ForeignKey(settings.AUTH_USER_MODEL)
    circle = models.ForeignKey(Circle)

    # this specifies whether the user is disabled or activated
    # private circle (favorite): whether the member is still in the circle
    # public circle: whether the member wants to be in the circle, or resigned.
    active = models.BooleanField(default=False)

    # whether the membership is approved by authorities or a panel.
    # private circle: should always be true, because private list are always approved by the owner. if the member doesn't want to be included, it could be set as false.
    # public circle: someone (either the owner or a panel) needs to approve the membership.
    # agency: usually should always be true. subscribers are always true.
    approved = models.NullBooleanField(default=None, blank=True, null=True)

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

    def is_pending_review(self):
        return self.approved is None

    def is_star(self):
        return self.is_admin() or self.type == Membership.Type.FAVORITE.value


class UserConnection(object):
    """
    This is about how two users are connected. Similar things are in Match. Might need to combine in the future.
    """
    def __init__(self, initiate_user, target_user, membership_list=[]):
        self.initiate_user = initiate_user
        self.target_user = target_user
        self.membership_list = membership_list       # this is the membership list that has "target_user" as members.

    def add_membership(self, membership):
        assert membership.member == self.target_user
        self.membership_list.append(membership)

    def get_circle_list(self):
        circle_count = defaultdict(int)
        for membership in self.membership_list:
            circle_count[membership.circle] += 1
        circle_list = [(k, v) for k, v in circle_count.items()]
        circle_sorted_by_count = [t[0] for t in sorted(circle_list, key=lambda l: l[1], reverse=True)]
        return circle_sorted_by_count
