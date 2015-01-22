# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20150116_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='phone_main',
            field=localflavor.us.models.PhoneNumberField(blank=True, max_length=20),
            preserve_default=True,
        ),
    ]
