# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('puser', '0002_puser'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='initiated',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='info',
            name='area',
            field=models.ForeignKey(default=1, to='puser.Area'),
        ),
    ]
