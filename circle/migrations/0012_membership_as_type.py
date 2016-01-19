# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0011_auto_20160113_0105'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='as_type',
            field=models.PositiveSmallIntegerField(default=None, choices=[(1, 'Spouse'), (2, 'Family'), (3, 'Neighbor'), (4, 'Colleague'), (5, 'Friend'), (6, 'Kidfriend')], null=True, blank=True),
        ),
    ]
