# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0010_auto_20151217_1251'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='supersetrel',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='supersetrel',
            name='child',
        ),
        migrations.RemoveField(
            model_name='supersetrel',
            name='parent',
        ),
        migrations.DeleteModel(
            name='ParentCircle',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='type',
        ),
        migrations.AlterField(
            model_name='circle',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Personal'), (2, 'Public')]),
        ),
        migrations.DeleteModel(
            name='SupersetRel',
        ),
    ]
