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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('type', models.PositiveSmallIntegerField(help_text='The type of the log entry.', choices=[(1, 'Update: offer regular'), (2, 'Update: offer date')])),
                ('ref', models.CommaSeparatedIntegerField(max_length=100, help_text='ID of the entity in question. Handled by the particular type.')),
                ('message', models.TextField(help_text='Addition human-readable message.', blank=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
