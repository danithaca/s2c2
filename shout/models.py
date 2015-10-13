from enum import Enum

from django.contrib.auth.models import User
from django.db import models

from circle.models import Circle
from contract.models import Contract
from shout.notify import notify_agent


class Shout(models.Model):
    class AudienceType(Enum):
        UNDEFINED = 0
        USER = 1
        CIRCLE = 2
        CONTRACT = 3
        ADMIN = 4
        # RESPONSE = 5      # this is the response to previous shout messages, and does not need to relate to any thing.
        MIXED = 99

    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    from_user = models.ForeignKey(User, related_name='from_user', blank=True, null=True)
    audience_type = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in AudienceType], default=AudienceType.UNDEFINED.value)

    to_users = models.ManyToManyField(User, related_name='to_user', blank=True)
    to_circles = models.ManyToManyField(Circle, blank=True)
    to_contracts = models.ManyToManyField(Contract, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    delivered = models.BooleanField(default=False)

    def deliver(self, force=False):
        if self.delivered and not force:
            return

        if self.audience_type == Shout.AudienceType.ADMIN.value:
            ctx = {'message': self.body}
            from_user = None
            if self.from_user:
                from_user = self.from_user
            notify_agent.send(from_user, None, 'shout/messages/shout_to_admin', ctx)

        if self.audience_type == Shout.AudienceType.USER.value:
            ctx = {'message': self.body}
            for to_user in self.to_users.all():
                notify_agent.send(self.from_user, to_user, 'shout/messages/shout_to_user', ctx)

        self.delivered = True
        self.save()
