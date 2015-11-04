# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [('shout', '0001_initial'), ('shout', '0002_auto_20150630_1050'), ('shout', '0003_auto_20150630_1129'), ('shout', '0004_auto_20150630_1130'), ('shout', '0005_auto_20150917_1300'), ('shout', '0006_auto_20150917_1516')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Shout',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('subject', models.CharField(max_length=200, blank=True)),
                ('body', models.TextField()),
                ('audience_type', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Undefined'), (1, 'User'), (2, 'Circle'), (3, 'Contract'), (4, 'Admin'), (99, 'Mixed')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('delivered', models.BooleanField(default=False)),
                ('to_circles', models.ManyToManyField(to='circle.Circle', blank=True)),
                ('to_contracts', models.ManyToManyField(to='contract.Contract', blank=True)),
                ('from_user', models.ForeignKey(related_name='from_user', blank=True, null=True, to=settings.AUTH_USER_MODEL)),
                ('to_users', models.ManyToManyField(related_name='to_user', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
    ]
