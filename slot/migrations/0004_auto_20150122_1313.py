# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slot', '0003_auto_20150116_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meet',
            name='need',
            field=models.OneToOneField(to='slot.NeedSlot', primary_key=True),
            preserve_default=True,
        ),
    ]
