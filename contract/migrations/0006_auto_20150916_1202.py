# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0005_auto_20150909_1011'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='audience_data',
            field=models.TextField(help_text='Extra data for the particular audience type, stored in JSON.', blank=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='audience_type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'Smart'), (2, 'Circle')]),
        ),
    ]
