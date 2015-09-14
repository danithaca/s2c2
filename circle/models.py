from enum import Enum
from django.db import models
from django.conf import settings

class Circle(models.Model):
    """
    Define the circles users could join.
    """

    class Type(Enum):
        PERSONAL = 1
        PUBLIC = 2
        AGENCY = 3
        SUPERSET = 4
        # SUBSCRIBER = 5    # people who suscribed to certain circles
        # LOOP = 6          # the circle of people who added me as favorite.

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    homepage = models.URLField(max_length=200, blank=True)

    type = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in Type])

    # the last resort to access someone in the circle. usually we'll use membership.
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner')
    created = models.DateTimeField(auto_now_add=True)

    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership')

    from location.models import Area
    # circle's listing area. doesn't necessarily mean every member in the circle have to be in the area
    area = models.ForeignKey(Area, default=1)

    def display(self):
        if self.type == Circle.Type.PERSONAL.value:
            name = self.owner.get_full_name() or self.owner.username
            return '%s\'s list' % name
        else:
            return self.name

    def __str__(self):
        return self.name

    def add_member(self, user, membership_type=None, approved=None):
        """
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

    def get_membership(self, user):
        return Membership.objects.get(member=user, circle=self)

    def get_active_member(self):
        return self.members.filter(membership__active=True)

    def is_type_personal(self):
        return self.type == Circle.Type.PERSONAL.value

    def is_type_public(self):
        return self.type == self.type == Circle.Type.PUBLIC.value

    def count(self, membership_type=None):
        qs = self.membership_set.filter(active=True, approved=True)
        if type is not None:
            qs.filter(type=membership_type)
        return qs.count()


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
    """

    class Type(Enum):
        NORMAL = 1
        ADMIN = 2
        PARTIAL = 3         # this is a passive membership that only receive notifications, e.g., subscribe to a agency circle
        HOMO = 4            # counted as the same user, or sharing the same kids.

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

    class Meta:
        # here we assume a user won't have multiple "membership" instances to the same circle.
        # relieving the assumption will affect many existing code
        unique_together = ('member', 'circle')

    def is_type_normal(self):
        return self.type == Membership.Type.NORMAL.value

    def is_type_partial(self):
        return self.type == Membership.Type.PARTIAL.value

    def __str__(self):
        return '%s (%s)' % (self.member.get_name(), self.circle.display())