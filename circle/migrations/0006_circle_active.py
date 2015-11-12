# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0005_circle_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
