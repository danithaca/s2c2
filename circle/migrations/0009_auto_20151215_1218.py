# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0008_auto_20151215_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circle',
            name='signup_code',
            field=models.OneToOneField(to='account.SignupCode', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True),
        ),
    ]
