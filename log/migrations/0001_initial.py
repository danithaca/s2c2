# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('type', models.PositiveSmallIntegerField(help_text='The type of the log entry.', choices=[(5, 'offer update'), (6, 'need update')])),
                ('ref', models.CommaSeparatedIntegerField(help_text='ID of the entity in question. Handled by the particular type.', max_length=100)),
                ('message', models.TextField(blank=True, help_text='Addition human-readable message.')),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('updated', models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 1, 9, 23, 1, 24, 997225, tzinfo=utc))),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('done', models.BooleanField(default=False)),
                ('level', models.SmallIntegerField(help_text='priority level of the notification.', choices=[(10, 'high'), (20, 'normal'), (30, 'low')])),
                ('log', models.ForeignKey(to='log.Log')),
                ('receiver', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='notification_receiver')),
                ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, related_name='notification_sender')),
                ('created', models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 1, 16, 16, 34, 34, 155364, tzinfo=utc))),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='log',
            name='type',
            field=models.PositiveSmallIntegerField(help_text='The type of the log entry.', choices=[(5, 'offer update'), (6, 'need update'), (7, 'meet updated')]),
            preserve_default=True,
        ),
    ]
