# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('puser', '0004_remove_info_initiated'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='homepage',
            field=models.URLField(blank=True),
        ),
    ]
