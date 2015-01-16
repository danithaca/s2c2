# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('log', '0004_auto_20150114_1233'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('done', models.BooleanField(default=False)),
                ('level', models.SmallIntegerField(choices=[(10, 'high'), (20, 'normal'), (30, 'low')], help_text='priority level of the notification.')),
                ('log', models.ForeignKey(to='log.Log')),
                ('receiver', models.ForeignKey(related_name='notification_receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(null=True, related_name='notification_sender', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='log',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(5, 'offer update'), (6, 'need update'), (7, 'meet updated')], help_text='The type of the log entry.'),
            preserve_default=True,
        ),
    ]
