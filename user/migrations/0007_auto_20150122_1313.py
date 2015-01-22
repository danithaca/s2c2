# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20150122_1309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='centers',
            field=models.ManyToManyField(blank=True, to='location.Center'),
            preserve_default=True,
        ),
    ]
