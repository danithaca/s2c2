# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='audience_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'Smart'), (2, 'Circle'), (3, 'Manual')]),
        ),
    ]
