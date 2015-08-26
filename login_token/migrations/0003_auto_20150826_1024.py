# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('login_token', '0002_token_accessed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='token',
            name='is_valid',
        ),
        migrations.AlterField(
            model_name='token',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
