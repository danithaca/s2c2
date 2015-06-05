# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('location', '0003_auto_20150421_1424'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('event_start', models.DateTimeField()),
                ('event_end', models.DateTimeField()),
                ('price', models.DecimalField(max_digits=5, decimal_places=2)),
                ('description', models.TextField(blank=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Initiated'), (2, 'Active'), (3, 'Confirmed'), (4, 'Finished'), (5, 'Canceled')], default=1)),
                ('area', models.ForeignKey(to='location.Area')),
                ('buyer', models.ForeignKey(related_name='buyer', to=settings.AUTH_USER_MODEL)),
                ('seller', models.ForeignKey(related_name='seller', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Initialized'), (2, 'Engaged'), (3, 'Declined'), (4, 'Accepted'), (5, 'Canceled')], default=1)),
                ('score', models.FloatField(default=0.0)),
                ('circles', models.ManyToManyField(to='circle.Circle')),
                ('contract', models.ForeignKey(to='contract.Contract')),
                ('target', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='match',
            unique_together=set([('contract', 'target')]),
        ),
    ]
