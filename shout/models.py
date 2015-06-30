from django.contrib.auth.models import User
from django.db import models
from enum import Enum
from circle.models import Circle
from contract.models import Contract


class Shout(models.Model):
    class Audience(Enum):
        UNDEFINED = 0
        USER = 1
        CIRCLE = 2
        CONTRACT = 3
        MIXED = 99

    subject = models.CharField(max_length=200)
    body = models.TextField()
    from_user = models.ForeignKey(User, related_name='from_user')
    audience = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in Audience], default=Audience.UNDEFINED.value)

    to_users = models.ManyToManyField(User, related_name='to_user', blank=True)
    to_circles = models.ManyToManyField(Circle, blank=True)
    to_contracts = models.ManyToManyField(Contract, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    delivered = models.BooleanField(default=False)
