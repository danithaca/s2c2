# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0002_log_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Update: offer regular'), (2, 'Update: offer date'), (3, 'Update: need regular'), (4, 'Update: need date')], help_text='The type of the log entry.'),
            preserve_default=True,
        ),
    ]
