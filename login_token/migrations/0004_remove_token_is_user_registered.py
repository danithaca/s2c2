# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login_token', '0003_auto_20150826_1024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='token',
            name='is_user_registered',
        ),
    ]
