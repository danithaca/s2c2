from enum import Enum
from django.contrib.auth.models import User
from django.db import models


class Circle(models.Model):
    """
    Define the circles users could join.
    """

    class Type(Enum):
        PERSONAL = 1
        PUBLIC = 2
        AGENCY = 3
        SUPERSET = 4
        # SUBSCRIBER = 5
        # LOOP = 6          # the circle of people who added me as favorite.

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    type = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in Type])

    # the last resort to access someone in the circle. usually we'll use membership.
    owner = models.ForeignKey(User, related_name='owner')
    created = models.DateTimeField(auto_now_add=True)

    members = models.ManyToManyField(User, through='Membership')

    from location.models import Area
    # circle's listing area. doesn't necessarily mean every member in the circle have to be in the area
    area = models.ForeignKey(Area, default=1)

    def display(self):
        if self.type == Circle.Type.PERSONAL.value:
            return '%s\'s circle' % self.owner.get_full_name() or self.ower.email
        else:
            return self.name

    def __str__(self):
        return self.name

    def add_member(self, user):
        """
        :return: if membership already exists, return it. otherwise, create the membership with default.
        """
        membership, created = Membership.objects.update_or_create(member=user, circle=self, defaults={'active': True})
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

    member = models.ForeignKey(User)
    circle = models.ForeignKey(Circle)

    # this specifies whether the user is disabled or activated
    # private circle (favorite): whether the member is still in the circle
    # public circle: whether the member wants to be in the circle, or resigned.
    active = models.BooleanField(default=False)

    # whether the membership is approved by authorities or a panel.
    # private circle: should always be true, because private list are always approved by the owner. if the member doesn't want to be included, it could be set as false.
    # public circle: someone (either the owner or a panel) needs to approve the membership.
    approved = models.BooleanField(default=False)

    # seems we don't need a "owner" type. the admin will suffice
    type = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in Type], default=Type.NORMAL.value)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        # here we assume a user won't have multiple "membership" instances to the same circle.
        # relieving the assumption will affect many existing code
        unique_together = ('member', 'circle')
