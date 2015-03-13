# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import slot.models


class Migration(migrations.Migration):

    dependencies = [
        ('slot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='needslot',
            name='day',
            field=slot.models.DayTokenField(db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='offerslot',
            name='day',
            field=slot.models.DayTokenField(db_index=True),
            preserve_default=True,
        ),
    ]
