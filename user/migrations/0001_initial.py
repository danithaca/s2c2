# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('location', '__first__'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FullUser',
            fields=[
                ('user_ptr', models.OneToOneField(to=settings.AUTH_USER_MODEL, parent_link=True, primary_key=True, serialize=False, auto_created=True)),
                ('address', models.CharField(max_length=200, blank=True)),
                ('phone_main', models.CharField(max_length=12, blank=True)),
                ('phone_backup', models.CharField(max_length=12, blank=True)),
                ('validated', models.NullBooleanField()),
                ('centers', models.ManyToManyField(to='location.Center')),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
                'abstract': False,
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('group_ptr', models.OneToOneField(to='auth.Group', parent_link=True, primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=50)),
                ('function_center', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=('auth.group',),
        ),
    ]
