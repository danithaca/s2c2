from enum import Enum
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from contract import tasks

class StatusMixin(object):
    """
    We assume the subclass has a 'Status' class and a 'status' field that initiate the Status class
    """

    # IMPORTANT: all status change should go through this for centralized trigger handling.
    def change_status(self, old_status, new_status):
        assert self.status == old_status, 'Status does not match: %s, %s' % (self.__class__.Status(old_status), self.__class__.Status(new_status))
        self.status = new_status
        self.save()


class Contract(StatusMixin, models.Model):
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

    initiate_user = models.ForeignKey(User)
    confirmed_match = models.OneToOneField('Match', blank=True, null=True, related_name='confirmed_contract')     # user string for classname per django doc.

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

    def hourly_rate(self):
        hours = (self.event_end - self.event_start).total_seconds() / 3600
        rate = float(self.price) / hours if hours > 0 else 0
        return round(Decimal(rate), 2)

    def activate(self):
        """
        Make the contract active after payment received; Non-blocking.
        """
        # quick and dirty approach is just to make call here directly.
        old_status = Contract.Status.INITIATED.value
        new_status = Contract.Status.ACTIVE.value
        self.change_status(old_status, new_status)

        # non-blocking process
        tasks.after_contract_activated.delay(self)

    def confirm(self, match):
        assert self.confirmed_match is None, 'Confirmed match already exists.'
        assert self == match.contract, 'Match object does not link to contract object.'
        self.confirmed_match = match
        self.change_status(Contract.Status.ACTIVE.value, Contract.Status.CONFIRMED.value)

    def cancel(self):
        assert self.status != Contract.Status.CANCELED.value, 'Contract already canceled.'
        old_status = self.status
        self.change_status(old_status, Contract.Status.CANCELED.value)

    def revert(self):
        """
        From confirmed status back to active
        """
        self.confirmed_match = None
        self.change_status(Contract.Status.CONFIRMED.value, Contract.Status.ACTIVE.value)

    def is_active(self):
        return self.status == Contract.Status.ACTIVE.value

    def is_confirmed(self):
        return self.status == Contract.Status.CONFIRMED.value

    def count_accepted_match(self):
        return Match.objects.filter(contract=self, status=Match.Status.ACCEPTED.value).count()

    def count_total_match(self):
        return Match.objects.filter(contract=self).count()


# this automatically activates the contract.
# todo: add payment step.
@receiver(post_save, sender=Contract)
def auto_activate(sender, **kwargs):
    instance = kwargs['instance']
    created = kwargs['created']
    if created and instance.status == Contract.Status.INITIATED.value:
        instance.activate()


class Match(StatusMixin, models.Model):
    """
    Given a contract, find the matched users for the contract.
    """

    class Status(Enum):
        INITIALIZED = 1         # just created, nothing more
        ENGAGED = 2             # notification has been sent. but no response
        DECLINED = 3            # the target user declined the request
        ACCEPTED = 4            # the target user accepted the request. doesn't mean the initiate_user selected the match
        CANCELED = 5            # the initiate_user canceled the match for some reason.

    contract = models.ForeignKey(Contract)
    target_user = models.ForeignKey(User)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    status = models.PositiveSmallIntegerField(choices=[(s.value, s.name.capitalize()) for s in Status], default=Status.INITIALIZED.value)

    # used for ranking, this is intentionally undefined and pertain to different algorithms
    score = models.FloatField(default=0.0)

    # the circles to which the target belongs that leads to the match.
    # doesn't necessarily links to the initiate_user's circle
    from circle.models import Circle
    circles = models.ManyToManyField(to=Circle)

    class Meta:
        unique_together = ('contract', 'target_user')

    def accept(self):
        old_status = self.status
        if old_status != Match.Status.ACCEPTED.value:
            self.change_status(old_status, Match.Status.ACCEPTED.value)
            # non-blocking. only executed when match is really accepted.
            tasks.after_match_accepted.delay(self)

    def decline(self):
        old_status = self.status
        if old_status != Match.Status.DECLINED.value:
            self.change_status(old_status, Match.Status.DECLINED.value)
        # seems we don't need to send notification if a match is declined.

    def is_accepted(self):
        return self.status == Match.Status.ACCEPTED.value


############################ signals ###############################

# signals should be declared in AppConfig.ready() according to https://docs.djangoproject.com/en/1.8/ref/signals/
# see also http://stackoverflow.com/questions/2719038/where-should-signal-handlers-live-in-a-django-project