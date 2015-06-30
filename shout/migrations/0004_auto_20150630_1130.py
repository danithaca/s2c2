# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shout', '0003_auto_20150630_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shout',
            name='to_contracts',
            field=models.ManyToManyField(to='contract.Contract', blank=True),
        ),
    ]
