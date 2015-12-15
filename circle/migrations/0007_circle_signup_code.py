# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20150902_1827'),
        ('circle', '0006_circle_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle',
            name='signup_code',
            field=models.ForeignKey(to='account.SignupCode', null=True, blank=True),
        ),
    ]
