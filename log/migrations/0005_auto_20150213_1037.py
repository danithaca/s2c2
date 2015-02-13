# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0004_auto_20150129_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(5, 'staff availability update'), (6, 'classroom need update'), (7, 'assignment update'), (16, 'assignment canceled due to staff availability change'), (17, 'assignment canceled due to classroom need change'), (11, 'staff template operation'), (11, 'classroom template operation'), (13, 'user signup'), (14, 'comment'), (15, 'user verification')], help_text='The type of the log entry.'),
            preserve_default=True,
        ),
    ]
