# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import slot.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('location', '0001_initial'),
        ('slot', '0001_squashed_0003_auto_20150112_2009'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetSlot',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('day', slot.models.DayTokenField()),
                ('start_time', slot.models.TimeTokenField()),
                ('end_time', slot.models.TimeTokenField()),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'inactive'), (1, 'main'), (20, 'backup')], default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NeedSlot',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('day', slot.models.DayTokenField()),
                ('start_time', slot.models.TimeTokenField()),
                ('end_time', slot.models.TimeTokenField()),
                ('location', models.ForeignKey(to='location.Location')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OfferSlot',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('day', slot.models.DayTokenField()),
                ('start_time', slot.models.TimeTokenField()),
                ('end_time', slot.models.TimeTokenField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='meetslot',
            name='need',
            field=models.ForeignKey(to='slot.NeedSlot'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='meetslot',
            name='offer',
            field=models.ForeignKey(to='slot.OfferSlot'),
            preserve_default=True,
        ),
    ]
