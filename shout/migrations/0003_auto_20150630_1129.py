# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('shout', '0002_auto_20150630_1050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shout',
            name='to_circles',
            field=models.ManyToManyField(blank=True, to='circle.Circle'),
        ),
        migrations.AlterField(
            model_name='shout',
            name='to_users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, related_name='to_user'),
        ),
    ]
