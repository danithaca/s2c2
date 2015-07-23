from datetime import timedelta
from django.utils import timezone
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

    # instead of polymorphism using the Contract/Match class, we want centralized handle here to make things read clear.
    def display_status(self):
        status = self.__class__.Status(self.status)

        contract_display_map = {
            Contract.Status.INITIATED: ('default', 'Inactive', ''),
            Contract.Status.ACTIVE: ('primary', 'Active', ''),
            Contract.Status.CONFIRMED: ('success', 'Active - Confirmed', ''),
            Contract.Status.SUCCESSFUL: ('info', 'Successful', ''),
            Contract.Status.CANCELED: ('warning', 'Canceled', ''),
            Contract.Status.FAILED: ('danger', 'Failed', ''),
        }

        match_display_map = {
            Match.Status.INITIALIZED: ('default', 'Waiting', ''),
            Match.Status.ENGAGED: ('info', 'Notified & Waiting', ''),
            Match.Status.ACCEPTED: ('primary', 'Accepted', ''),
            Match.Status.DECLINED: ('warning', 'Declined', ''),
            Match.Status.CANCELED: ('danger', 'Canceled', ''),
        }

        if isinstance(self, Contract):
            color, label, explanation = contract_display_map.get(status, ('default', str(status).capitalize(), ''))
            # override
            # special handle for expired stuff
            if self.is_event_expired():
                if status in (Contract.Status.INITIATED, Contract.Status.ACTIVE):
                    color, label = 'warning', 'Expired'
                if status == Contract.Status.CONFIRMED:
                    color, label = 'info', 'Done'
            # not expired, proceed as normal
            else:
                if status == Contract.Status.ACTIVE:
                    if not self.match_set.filter(status=Match.Status.ACCEPTED.value).exists():
                        label = 'Active - Waiting'
                    else:
                        label, explanation = 'Active - Found', 'The client has found at least 1 person who agreed to be a server. The client has not confirmed yet.'

        elif isinstance(self, Match):
            color, label, explanation = match_display_map.get(status, ('default', str(status).capitalize(), ''))
            # override
            if self.contract.is_event_expired() and status in (Match.Status.INITIALIZED, Match.Status.ENGAGED):
                    color, label = 'warning', 'Expired'
            elif status == Match.Status.ACCEPTED:
                if self.contract.confirmed_match == self:
                    color, label = 'success', 'Accepted & Confirmed'
                elif self.contract.is_confirmed():
                    color, label, explanation = 'primary', 'Not chosen', 'The server accepted your request but you did not choose him/her to serve you.'
                elif not self.contract.is_event_expired() and not self.contract.is_confirmed():
                    color, label = 'primary', 'Accepted & Pending'

        else:
            assert False

        return {'color': color, 'label': label, 'explanation': explanation}


class Contract(StatusMixin, models.Model):
    """
    Handles parents looking for sitters.
    """

    class Status(Enum):
        INITIATED = 1       # just created. no payment, etc.
        ACTIVE = 2          # payment posted, matching in process
        CONFIRMED = 3       # found someone, and both parties agree to the work.
        SUCCESSFUL = 4      # after the contract, everyone are happy.
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

    def __str__(self):
        return 'Contract: %d' % self.id

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

        # todo: non-blocking process
        # tasks.after_contract_activated.delay(self)
        # make it blocking to make sure there are some matches.
        tasks.after_contract_activated(self)

    def confirm(self, match):
        assert self.confirmed_match is None, 'Confirmed match already exists.'
        assert self == match.contract, 'Match object does not link to contract object.'
        self.confirmed_match = match
        self.change_status(Contract.Status.ACTIVE.value, Contract.Status.CONFIRMED.value)

        # non-blocking: send messages
        tasks.after_contract_confirmed.delay(self)

    def cancel(self):
        assert self.status != Contract.Status.CANCELED.value, 'Contract already canceled.'
        old_status = self.status
        self.change_status(old_status, Contract.Status.CANCELED.value)

    def succeed(self):
        assert self.status == Contract.Status.CONFIRMED.value, 'Contract not in confirmed status.'
        old_status = self.status
        self.change_status(old_status, Contract.Status.SUCCESSFUL.value)

    def fail(self):
        assert self.status == Contract.Status.CONFIRMED.value, 'Contract not in confirmed status.'
        old_status = self.status
        self.change_status(old_status, Contract.Status.FAILED.value)

    def revert(self):
        """
        From confirmed status back to active
        """
        assert self.confirmed_match is not None, 'No confirmed match. Cannot revert.'
        old_confirmed_match = self.confirmed_match
        self.confirmed_match = None
        self.change_status(Contract.Status.CONFIRMED.value, Contract.Status.ACTIVE.value)
        tasks.after_contract_reverted.delay(self, old_confirmed_match)

    def is_active(self):
        return self.status == Contract.Status.ACTIVE.value

    def is_confirmed(self):
        return self.status == Contract.Status.CONFIRMED.value

    def count_accepted_match(self):
        return Match.objects.filter(contract=self, status=Match.Status.ACCEPTED.value).count()

    def count_declined_match(self):
        return Match.objects.filter(contract=self, status=Match.Status.DECLINED.value).count()

    def count_total_match(self):
        return Match.objects.filter(contract=self).count()

    def event_length(self):
        return self.event_end - self.event_start

    def is_event_expired(self):
        # fixme: make sure tz is fine
        return timezone.now() > self.event_end

    def is_event_happening(self):
        return self.event_start <= timezone.now() <= self.event_end

    def is_event_same_day(self):
        return self.event_start.date() == self.event_end.date()

    def display_event_length(self):
        assert self.event_end >= self.event_start
        diff = self.event_end - self.event_start
        result = ''
        if diff.days:
            result = '%d day%s' % (diff.days, 's' if diff.days > 1 else '')
            if diff.seconds:
                hours = round(diff.seconds / 3600)
                if hours:
                    result += ' %d hour%s' % (hours, 's' if hours > 1 else '')
        elif diff.seconds:
            total_minutes = round(diff.seconds / 60)
            hours, minutes = divmod(total_minutes, 60)
            if hours:
                result += '%d hour%s ' % (hours, 's' if hours > 1 else '')
            if minutes:
                result += '%d minute%s' % (minutes, 's' if minutes > 1 else '')
        if result:
            return result.strip()
        else:
            return 'a few seconds'

    def display_event_range(self):
        get_time = lambda t: t.strftime('%H:%M')
        get_fulltime = lambda t: t.strftime('%H:%M %b. %d')
        if self.is_event_same_day():
            return '%s~%s, %s' % (get_time(self.event_start), get_time(self.event_end), self.event_start.strftime('%b. %d'))
        else:
            return '%s ~ %s' % (get_fulltime(self.event_start), get_fulltime(self.event_end))



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

    def get_absolute_url(self):
        return reverse('contract:match_view', kwargs={'pk': self.pk})

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

    def is_declined(self):
        return self.status == Match.Status.DECLINED.value

    def is_confirmed(self):
        return self == self.contract.confirmed_match

    def engage(self):
        """
        shout to the targeted user and engage him/her for this match.
        """
        old_status = self.status
        if old_status == Match.Status.INITIALIZED.value:
            new_status = Match.Status.ENGAGED.value
            self.change_status(old_status, new_status)

            # non-blocking process
            tasks.after_match_engaged.delay(self)

    # def get_puser_pair(self):
    #     from puser.models import PUser
    #     return PUser.from_user(self.contract.initiate_user), PUser.from_user(self.target_user)

    def count_served(self):
        from puser.models import PUser
        return PUser.from_user(self.target_user).count_served(self.contract.initiate_user)

    def count_served_reverse(self):
        from puser.models import PUser
        return PUser.from_user(self.contract.initiate_user).count_served(self.target_user)


class Engagement(object):
    """
    This is a single match or a contract without a match. Shown at the homepage.
    """
    def __init__(self):
        self.contract = None
        self.match = None
        self.initiate_user = None
        self.target_user = None
        self.main_user = None           # the user on whom this engagement is focused. could be either the initiate_user or the target_user

    @staticmethod
    def from_contract(contract):
        assert isinstance(contract, Contract)
        e = Engagement()
        e.main_user = contract.initiate_user
        e.contract = contract
        e.initiate_user = contract.initiate_user
        if contract.confirmed_match:
            e.match = contract.confirmed_match
            e.target_user = contract.confirmed_match.target_user
        return e

    @staticmethod
    def from_match(match):
        assert isinstance(match, Match)
        e = Engagement()
        e.main_user = match.target_user
        e.contract = match.contract
        e.initiate_user = match.contract.initiate_user
        e.match = match
        e.target_user = match.target_user
        return e

    # todo: polish this one.
    def get_status(self):
        if self.is_main_contract():
            return Contract.Status(self.contract.status).name.capitalize()
        else:
            assert self.is_main_match()
            return Match.Status(self.match.status).name.capitalize()

    def display_status(self):
        if self.is_main_contract():
            return self.contract.display_status()
        else:
            assert self.is_main_match()
            return self.match.display_status()

    def get_link(self):
        if self.is_main_contract():
            return self.contract.get_absolute_url()
        else:
            assert self.is_main_match()
            return self.match.get_absolute_url()

    def is_main_contract(self):
        return self.main_user == self.initiate_user

    def is_main_match(self):
        return self.main_user == self.target_user

############################ signals ###############################

# todo: signals should be declared in AppConfig.ready() according to https://docs.djangoproject.com/en/1.8/ref/signals/
# see also http://stackoverflow.com/questions/2719038/where-should-signal-handlers-live-in-a-django-project


# this automatically activates the contract.
# todo: add payment step.
@receiver(post_save, sender=Contract)
def contract_auto_activate(sender, **kwargs):
    instance = kwargs['instance']
    created = kwargs['created']
    if created and instance.status == Contract.Status.INITIATED.value:
        instance.activate()


@receiver(post_save, sender=Match)
def match_auto_engage(sender, **kwargs):
    instance = kwargs['instance']
    created = kwargs['created']
    # only do it when the match was first created.
    if created and instance.status == Match.Status.INITIALIZED.value:
        instance.engage()
