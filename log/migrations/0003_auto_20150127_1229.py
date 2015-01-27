# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0002_auto_20150127_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='type',
            field=models.PositiveSmallIntegerField(help_text='The type of the log entry.', choices=[(5, 'offer update'), (6, 'need update'), (7, 'meet update'), (16, 'meet cascade delete offer'), (17, 'meet cascade delete need')]),
            preserve_default=True,
        ),
    ]
