# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0002_auto_20151109_1504'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membership',
            name='as_parent',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='as_sitter',
        ),
        migrations.AddField(
            model_name='membership',
            name='as_role',
            field=models.PositiveSmallIntegerField(default=7, choices=[(7, 'Parent'), (8, 'Sitter')]),
        ),
    ]
