# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0003_auto_20150112_2009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(5, 'offer update'), (6, 'need update')], help_text='The type of the log entry.'),
            preserve_default=True,
        ),
    ]
