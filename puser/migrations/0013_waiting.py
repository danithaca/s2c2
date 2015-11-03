# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('puser', '0012_auto_20151102_1301'),
    ]

    operations = [
        migrations.CreateModel(
            name='Waiting',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, to='puser.PUser', null=True, default=None)),
            ],
        ),
    ]
