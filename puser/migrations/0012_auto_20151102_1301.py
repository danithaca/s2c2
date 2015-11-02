# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('puser', '0011_auto_20151030_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='phone_backup',
            field=localflavor.us.models.PhoneNumberField(help_text='Phone number added by other people', blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='info',
            name='registered',
            field=models.BooleanField(default=True),
        ),
    ]
