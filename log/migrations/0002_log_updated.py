# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='updated',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 1, 9, 23, 1, 24, 997225, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
