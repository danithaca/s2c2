# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='template_base_date',
            field=models.DateField(help_text='Pick a date whose week schedule would be the template for automatic copy.', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='classroom',
            name='template_copy_ahead',
            field=models.CharField(help_text='How much ahead to copy the template.', choices=[('none', 'None'), ('1week', '1 Week'), ('2week', '2 Weeks'), ('3week', '3 Weeks'), ('4week', '4 Weeks')], max_length=10, default='none'),
            preserve_default=True,
        ),
    ]
