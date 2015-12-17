# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0009_auto_20151215_1218'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle',
            name='mark_agency',
            field=models.BooleanField(help_text='Whether this circle is "Agency". Only valid for public circles.', default=False),
        ),
        migrations.AddField(
            model_name='circle',
            name='mark_approved',
            field=models.NullBooleanField(help_text='Whether this circle is approved by site admins. Only valid for public circles.', default=None),
        ),
    ]
