from django.db import models
from django.contrib.auth.models import User


class Log(models.Model):
    TYPE_OFFER_REGULAR_UPDATE = 1
    LOG_TYPE = (
        (TYPE_OFFER_REGULAR_UPDATE, 'Update: offer regular')
    )
    creator = models.ForeignKey(User)
    type = models.PositiveSmallIntegerField(choices=LOG_TYPE, help_text='The type of the log entry.')
    ref_id = models.IntegerField(help_text='ID of the entity in question. Handled by the particular type.')
    message = models.TextField(blank=True, help_text='Addition human-readable message.')