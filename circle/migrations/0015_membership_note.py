# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0014_auto_20151005_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='note',
            field=models.TextField(blank=True),
        ),
    ]
