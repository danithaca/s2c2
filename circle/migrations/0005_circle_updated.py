# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0004_personalcircle_publiccircle'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 12, 16, 2, 51, 446446, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
