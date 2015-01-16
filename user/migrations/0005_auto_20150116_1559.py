# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_profile_area'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='phone_backup',
            field=localflavor.us.models.PhoneNumberField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone_main',
            field=localflavor.us.models.PhoneNumberField(max_length=20),
            preserve_default=True,
        ),
    ]
