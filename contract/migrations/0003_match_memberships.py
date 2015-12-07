# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0006_circle_active'),
        ('contract', '0002_auto_20151119_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='memberships',
            field=models.ManyToManyField(to='circle.Membership'),
        ),
    ]
