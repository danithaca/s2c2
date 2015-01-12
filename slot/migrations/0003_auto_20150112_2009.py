# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slot', '0002_meetinfo'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MeetInfo',
        ),
        migrations.AddField(
            model_name='meetdate',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'inactive'), (1, 'main'), (20, 'backup')], default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='meetregular',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'inactive'), (1, 'main'), (20, 'backup')], default=0),
            preserve_default=True,
        ),
    ]
