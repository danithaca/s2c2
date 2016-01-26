# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puser', '0002_auto_20151106_1730'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='private_note',
            field=models.TextField(blank=True),
        ),
    ]
