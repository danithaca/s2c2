# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0003_auto_20151110_1333'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalCircle',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('circle.circle',),
        ),
        migrations.CreateModel(
            name='PublicCircle',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('circle.circle',),
        ),
    ]
