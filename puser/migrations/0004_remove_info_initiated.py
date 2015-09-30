# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('puser', '0003_auto_20150612_1518'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='info',
            name='initiated',
        ),
    ]
