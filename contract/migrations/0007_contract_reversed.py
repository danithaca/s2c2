# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0006_auto_20150916_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='reversed',
            field=models.BooleanField(default=False),
        ),
    ]
