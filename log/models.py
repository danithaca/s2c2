from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User


# specifies when to create a new log entry or when to update instead.
NO_UPDATE_INTERVAL = timedelta(hours=2)


class Log(models.Model):
    TYPE_OFFER_REGULAR_UPDATE = 1
    TYPE_OFFER_DATE_UPDATE = 2

    LOG_TYPE = (
        (TYPE_OFFER_REGULAR_UPDATE, 'Update: offer regular'),
        (TYPE_OFFER_DATE_UPDATE, 'Update: offer date'),
    )

    creator = models.ForeignKey(User)
    type = models.PositiveSmallIntegerField(choices=LOG_TYPE, help_text='The type of the log entry.')
    ref = models.CommaSeparatedIntegerField(help_text='ID of the entity in question. Handled by the particular type.', max_length=100)
    message = models.TextField(blank=True, help_text='Addition human-readable message.')
    updated = models.DateTimeField(auto_now_add=True)


def log_offer_regular_update(creator, target_user, target_dow, message=None):
    entry = Log(creator=creator, type=Log.TYPE_OFFER_DATE_UPDATE, ref='%d,%d' % (target_user.pk, target_dow), message=message)
    entry.save()