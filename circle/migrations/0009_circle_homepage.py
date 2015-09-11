# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0008_auto_20150911_1025'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle',
            name='homepage',
            field=models.URLField(blank=True),
        ),
    ]
