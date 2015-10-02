# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0012_auto_20150930_1335'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParentCircle',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('circle.circle',),
        ),
    ]
