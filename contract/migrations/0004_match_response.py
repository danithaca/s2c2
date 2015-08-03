# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0003_auto_20150618_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='response',
            field=models.TextField(blank=True),
        ),
    ]
