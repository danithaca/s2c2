# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0007_auto_20150714_0907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='approved',
            field=models.NullBooleanField(default=None),
        ),
    ]
