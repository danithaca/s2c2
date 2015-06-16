from enum import Enum
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models


class Contract(models.Model):
    """
    Handles parents looking for sitters.
    """

    class Status(Enum):
        INITIATED = 1       # just created. no payment, etc.
        ACTIVE = 2          # payment posted, matching in process
        CONFIRMED = 3       # found someone, and both parties agree to the work.
        SUCCESSFUL = 4        # after the contract, everyone are happy.
        CANCELED = 5        # for some reason this was canceled.
        FAILED = 6          # was confirmed, but not carried through.

    buyer = models.ForeignKey(User, related_name='buyer')
    seller = models.ForeignKey(User, related_name='seller', blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    price = models.DecimalField(max_digits=5, decimal_places=2)

    # more details about the contract.
    description = models.TextField(blank=True)

    status = models.PositiveSmallIntegerField(choices=[(s.value, s.name.capitalize()) for s in Status], default=Status.INITIATED.value)

    # where does this contract happens. this is the ultimate place to decide where a contract goes
    from location.models import Area
    area = models.ForeignKey(Area)

    def get_absolute_url(self):
        return reverse('contract:view', kwargs={'pk': self.pk})

    def change_status(self, old_status, new_status):
        assert self.status == old_status, 'Status does not match: %s, %s' % (Contract.Status(old_status), Contract.Status(new_status))
        self.status = new_status
        self.save()

    def activate(self):
        """
        Make the contract active after payment received.
        """

        # someday: use signals/MQ instead.
        # quick and dirty approach is just to make call here directly.
        old_status = Contract.Status.INITIATED.value
        new_status = Contract.Status.ACTIVE.value
        self.change_status(old_status, new_status)

        from contract.algorithms import L1Recommender
        recommender = L1Recommender()
        recommender.recommend(self)


class Match(models.Model):
    """
    Given a contract, find the matched users for the contract.
    """

    class Status(Enum):
        INITIALIZED = 1         # just created, nothing more
        ENGAGED = 2             # notification has been sent. but no response
        DECLINED = 3            # the target user declined the request
        ACCEPTED = 4            # the target user accepted the request. doesn't mean the buyer selected the match
        CANCELED = 5            # the buyer canceled the match for some reason.

    contract = models.ForeignKey(Contract)
    target_user = models.ForeignKey(User)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    status = models.PositiveSmallIntegerField(choices=[(s.value, s.name.capitalize()) for s in Status], default=Status.INITIALIZED.value)

    # used for ranking, this is intentionally undefined and pertain to different algorithms
    score = models.FloatField(default=0.0)

    # the circles to which the target belongs that leads to the match.
    # doesn't necessarily links to the buyer's circle
    from circle.models import Circle
    circles = models.ManyToManyField(to=Circle)

    class Meta:
        unique_together = ('contract', 'target_user')