# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0003_auto_20150618_1543'),
        ('circle', '0006_auto_20150612_1729'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Shout',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('subject', models.CharField(max_length=200)),
                ('body', models.TextField()),
                ('audience', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Undefined'), (1, 'User'), (2, 'Circle'), (3, 'Contract'), (99, 'Mixed')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('delivered', models.BooleanField(default=False)),
                ('circles', models.ManyToManyField(to='circle.Circle')),
                ('contracts', models.ManyToManyField(to='contract.Contract')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
