# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shout', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shout',
            old_name='circles',
            new_name='to_circles',
        ),
        migrations.RenameField(
            model_name='shout',
            old_name='contracts',
            new_name='to_contracts',
        ),
        migrations.RemoveField(
            model_name='shout',
            name='users',
        ),
        migrations.AddField(
            model_name='shout',
            name='from_user',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL, related_name='from_user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shout',
            name='to_users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='to_user'),
        ),
    ]
