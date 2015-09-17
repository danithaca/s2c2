# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('shout', '0005_auto_20150917_1300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shout',
            name='audience_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Undefined'), (1, 'User'), (2, 'Circle'), (3, 'Contract'), (4, 'Admin'), (99, 'Mixed')]),
        ),
        migrations.AlterField(
            model_name='shout',
            name='from_user',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='from_user', blank=True),
        ),
    ]
