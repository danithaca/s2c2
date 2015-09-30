# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('puser', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PUser',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
