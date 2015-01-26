# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import slot.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meet',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NeedSlot',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
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
            model_name='meet',
            name='need',
            field=models.OneToOneField(to='slot.NeedSlot'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='meet',
            name='offer',
            field=models.OneToOneField(to='slot.OfferSlot'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='meet',
            unique_together=set([('offer', 'need')]),
        ),
    ]
