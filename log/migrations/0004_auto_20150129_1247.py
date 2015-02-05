# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0003_auto_20150127_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='type',
            field=models.PositiveSmallIntegerField(help_text='The type of the log entry.', choices=[(5, 'staff availability update'), (6, 'classroom need update'), (7, 'assignment update'), (16, 'assignment canceled due to staff availability change'), (17, 'assignment canceled due to classroom need change'), (11, 'staff template operation'), (11, 'classroom template operation'), (13, 'user signup'), (14, 'user comment'), (15, 'user verification')]),
            preserve_default=True,
        ),
    ]
