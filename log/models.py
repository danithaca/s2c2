from datetime import timedelta
import warnings

from django.db import models
from django.contrib.auth.models import User


# specifies when to create a new log entry or when to update instead.
from location.models import Location
from user.models import UserProfile
from django.utils import timezone


NO_UPDATE_INTERVAL = timedelta(hours=2)


class Log(models.Model):
    # OFFER_REGULAR_UPDATE = 1   # obsolete
    # OFFER_DATE_UPDATE = 2      # obsolete
    # NEED_REGULAR_UPDATE = 3    # obsolete
    # NEED_DATE_UPDATE = 4       # obsolete

    OFFER_UPDATE = 5
    NEED_UPDATE = 6

    MEET_UPDATE = 7
    # MEET_ADD = 8
    # MEET_DELETE = 9
    MEET_DELETE_CASCADE = 10

    # this implies it's "offer" update
    TEMPLATE_OP_STAFF = 11
    # this implies it's "need/meet" update
    TEMPLATE_OP_CLASSROOM = 12

    SIGNUP = 13
    COMMENT = 14
    VERIFY = 15

    LOG_TYPE = (
        # (TYPE_OFFER_REGULAR_UPDATE, 'Update: offer regular'),
        # (TYPE_OFFER_DATE_UPDATE, 'Update: offer date'),
        # (TYPE_NEED_REGULAR_UPDATE, 'Update: need regular'),
        # (TYPE_NEED_DATE_UPDATE, 'Update: need date'),
        (OFFER_UPDATE, 'offer update'),
        (NEED_UPDATE, 'need update'),
        (MEET_UPDATE, 'meet update'),
        (MEET_DELETE_CASCADE, 'meet delete cascade'),
    )

    creator = models.ForeignKey(User)
    type = models.PositiveSmallIntegerField(choices=LOG_TYPE, help_text='The type of the log entry.')
    ref = models.CommaSeparatedIntegerField(help_text='ID of the entity in question. Handled by the particular type.', max_length=100)
    message = models.TextField(blank=True, help_text='Addition human-readable message.')
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s: %s (%s)' % (self.creator.username, self.ref, self.get_type_display())

    def display(self):
        # if self.type == Log.OFFER_UPDATE:
        #     return 'updated availability (%s)' % self.message
        # elif self.type == Log.NEED_UPDATE:
        #     return 'updated needs: %s' % self.message
        return self.message

    @staticmethod
    def create(t, creator, data, message=None, force=False):
        from slot.models import DayToken, TimeToken
        ref = None
        if t in (Log.OFFER_UPDATE, Log.NEED_UPDATE):
            target, day = data
            assert isinstance(target, User) or isinstance(target, UserProfile) or isinstance(target, Location)
            assert isinstance(day, DayToken)
            ref = '%d,%s' % (target.pk, day.get_token())
        elif t == Log.MEET_UPDATE:
            staff, classroom, day, start_time = data
            assert isinstance(staff, User) and isinstance(classroom, Location) and isinstance(day, DayToken) and isinstance(start_time, TimeToken)
            ref = '%d,%d,%s,%s' % (staff.pk, classroom.pk, day.get_token(), start_time.get_token())
        elif t in (Log.TEMPLATE_OP_STAFF, Log.TEMPLATE_OP_CLASSROOM):
            target, day = data
            assert isinstance(target, User) or isinstance(target, Location)
            assert isinstance(day, DayToken) and not day.is_regular()
            ref = '%d,%s' % (target.pk, day.get_token())

        # todo: create or update based on time elapse.
        entry = Log(creator=creator, type=t, ref=ref, message=message)
        entry.save()

    def is_today(self):
        return timezone.now().date() == self.updated.date()


class Notification(models.Model):
    sender = models.ForeignKey(User, null=True, blank=True, related_name='notification_sender')
    receiver = models.ForeignKey(User, related_name='notification_receiver')
    # this is required, which means every notification would have a log, not vice versa.
    log = models.ForeignKey(Log)
    done = models.BooleanField(default=False)       # mark whether the receiver has viewed it or not.

    LEVEL_HIGH = 10
    LEVEL_NORMAL = 20
    LEVEL_LOW = 30
    LEVELS = (
        (LEVEL_HIGH, 'high'),
        (LEVEL_NORMAL, 'normal'),
        (LEVEL_LOW, 'low'),
    )
    level = models.SmallIntegerField(choices=LEVELS, help_text='priority level of the notification.')

    created = models.DateTimeField(auto_now_add=True)


def log_offer_update(creator, target_user, day, message=None):
    warnings.warn('Use Log::create() instead.', DeprecationWarning)
    # this gets called by views functions because we need to track the "creator".
    # fixme: add logic that update by interval instead of create new entry.
    entry = Log(creator=creator, type=Log.OFFER_UPDATE, ref='%d,%d' % (target_user.pk, int(day.get_token())), message=message)
    entry.save()


def log_need_update(creator, location, day, message=None):
    warnings.warn('Use Log::create() instead.', DeprecationWarning)
    entry = Log(creator=creator, type=Log.NEED_UPDATE, ref='%d,%d' % (location.pk, int(day.get_token())), message=message)
    entry.save()