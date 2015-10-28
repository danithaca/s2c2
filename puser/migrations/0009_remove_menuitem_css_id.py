# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('puser', '0008_auto_20151027_1552'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menuitem',
            name='css_id',
        ),
    ]
