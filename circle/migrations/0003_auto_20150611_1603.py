# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0002_auto_20150611_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circle',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Personal'), (2, 'Public'), (3, 'Agency'), (4, 'Superset')]),
        ),
    ]
