# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0013_auto_20160119_0058'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='private_note',
            field=models.TextField(blank=True),
        ),
    ]
