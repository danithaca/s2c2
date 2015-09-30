# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0011_auto_20150930_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circle',
            name='area',
            field=models.ForeignKey(to='puser.Area'),
        ),
    ]
