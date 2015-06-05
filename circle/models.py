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
        # SUPERSET = 4
        # SUBSCRIBER = 5

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    type = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in Type])

    # the last resort to access someone in the circle. usually we'll use membership.
    creator = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)

    from location.models import Area
    # circle's listing area. doesn't necessarily mean every member in the circle have to be in the area
    area = models.ForeignKey(Area)


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
    active = models.BooleanField(default=False)

    # seems we don't need a "owner" type. the admin will suffice
    type = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in Type], default=Type.NORMAL.value)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
