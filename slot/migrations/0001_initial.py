# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import slot.models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NeedSlot',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
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
        migrations.CreateModel(
            name='Meet',
            fields=[
                ('need', models.OneToOneField(primary_key=True, to='slot.NeedSlot')),
                ('offer', models.OneToOneField(primary_key=True, to='slot.OfferSlot')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
