# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('address', models.CharField(max_length=200, blank=True)),
                ('phone_main', models.CharField(max_length=12)),
                ('phone_backup', models.CharField(max_length=12, blank=True)),
                ('verified', models.NullBooleanField()),
                ('centers', models.ManyToManyField(to='location.Center')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('group', models.OneToOneField(primary_key=True, serialize=False, to='auth.Group')),
                ('machine_name', models.SlugField()),
                ('type_center', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
