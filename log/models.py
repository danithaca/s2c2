from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User


# specifies when to create a new log entry or when to update instead.
NO_UPDATE_INTERVAL = timedelta(hours=2)


class Log(models.Model):
    TYPE_OFFER_REGULAR_UPDATE = 1   # obsolete
    TYPE_OFFER_DATE_UPDATE = 2      # obsolete
    TYPE_NEED_REGULAR_UPDATE = 3    # obsolete
    TYPE_NEED_DATE_UPDATE = 4       # obsolete

    TYPE_OFFER_UPDATE = 5
    TYPE_NEED_UPDATE = 6

    LOG_TYPE = (
        # (TYPE_OFFER_REGULAR_UPDATE, 'Update: offer regular'),
        # (TYPE_OFFER_DATE_UPDATE, 'Update: offer date'),
        # (TYPE_NEED_REGULAR_UPDATE, 'Update: need regular'),
        # (TYPE_NEED_DATE_UPDATE, 'Update: need date'),
        (TYPE_OFFER_UPDATE, 'offer update'),
        (TYPE_NEED_UPDATE, 'need update'),
    )

    creator = models.ForeignKey(User)
    type = models.PositiveSmallIntegerField(choices=LOG_TYPE, help_text='The type of the log entry.')
    ref = models.CommaSeparatedIntegerField(help_text='ID of the entity in question. Handled by the particular type.', max_length=100)
    message = models.TextField(blank=True, help_text='Addition human-readable message.')
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s: %s (%s)' % (self.creator.username, self.ref, self.get_type_display())


def log_offer_update(creator, target_user, day, message=None):
    # this gets called by views functions because we need to track the "creator".
    # fixme: add logic that update by interval instead of create new entry.
    entry = Log(creator=creator, type=Log.TYPE_OFFER_UPDATE, ref='%d,%d' % (target_user.pk, int(day.get_token())), message=message)
    entry.save()


def log_need_update(creator, location, day, message=None):
    entry = Log(creator=creator, type=Log.TYPE_NEED_UPDATE, ref='%d,%d' % (location.pk, int(day.get_token())), message=message)
    entry.save()