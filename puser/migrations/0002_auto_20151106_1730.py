# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('puser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='enable_sms',
            field=models.BooleanField(help_text='Whether to receive SMS for important notifications.', default=False),
        ),
        migrations.AlterField(
            model_name='info',
            name='role',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(7, 'Parent'), (8, 'Sitter'), (11, 'Hybrid')], null=True),
        ),
    ]
