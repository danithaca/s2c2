# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0004_match_response'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Initiated'), (2, 'Active'), (3, 'Confirmed'), (4, 'Successful'), (5, 'Canceled'), (6, 'Failed'), (7, 'Expired')], default=1),
        ),
    ]
