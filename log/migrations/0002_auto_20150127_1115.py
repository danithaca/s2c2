# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(5, 'offer update'), (6, 'need update'), (7, 'meet update'), (10, 'meet delete cascade')], help_text='The type of the log entry.'),
            preserve_default=True,
        ),
    ]
