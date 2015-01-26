# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.PositiveSmallIntegerField(choices=[(5, 'offer update'), (6, 'need update'), (7, 'meet updated')], help_text='The type of the log entry.')),
                ('ref', models.CommaSeparatedIntegerField(max_length=100, help_text='ID of the entity in question. Handled by the particular type.')),
                ('message', models.TextField(blank=True, help_text='Addition human-readable message.')),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('done', models.BooleanField(default=False)),
                ('level', models.SmallIntegerField(choices=[(10, 'high'), (20, 'normal'), (30, 'low')], help_text='priority level of the notification.')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('log', models.ForeignKey(to='log.Log')),
                ('receiver', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='notification_receiver')),
                ('sender', models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL, related_name='notification_sender')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
