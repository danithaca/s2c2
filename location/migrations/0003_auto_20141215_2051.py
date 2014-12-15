# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0002_auto_20141215_2046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='address',
            field=models.CharField(max_length=200, blank=True),
            preserve_default=True,
        ),
    ]
