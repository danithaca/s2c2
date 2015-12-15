# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0007_circle_signup_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circle',
            name='signup_code',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='account.SignupCode'),
        ),
    ]
