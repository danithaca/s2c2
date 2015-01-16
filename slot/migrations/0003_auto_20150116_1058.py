# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slot', '0002_auto_20150114_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meet',
            name='need',
            field=models.OneToOneField(primary_key=True, serialize=False, to='slot.NeedSlot'),
            preserve_default=True,
        ),
    ]
