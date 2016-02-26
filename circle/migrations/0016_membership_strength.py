# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0015_auto_20160126_0142'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='strength',
            field=models.FloatField(default=0.5),
        ),
    ]
