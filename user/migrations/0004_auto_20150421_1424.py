# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20150421_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='template_base_date',
            field=models.DateField(help_text='Pick a date of which the weekly schedule would be the template for automatic copy.', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='template_copy_ahead',
            field=models.CharField(help_text='How much ahead to copy the template.', max_length=10, choices=[('none', 'None'), ('1week', '1 week ahead'), ('2week', '2 weeks ahead'), ('3week', '3 weeks ahead'), ('4week', '4 weeks ahead')], default='none'),
            preserve_default=True,
        ),
    ]
