# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('puser', '0006_auto_20150930_1345'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='role',
            field=models.PositiveSmallIntegerField(choices=[(7, 'Parent'), (8, 'Sitter')], null=True, blank=True),
        ),
    ]
