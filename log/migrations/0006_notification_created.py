# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0005_auto_20150116_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 1, 16, 16, 34, 34, 155364, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
