# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0003_auto_20150421_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
