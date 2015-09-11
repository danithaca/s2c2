# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0009_circle_homepage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Normal'), (2, 'Admin'), (3, 'Partial'), (4, 'Homo')], default=1),
        ),
    ]
