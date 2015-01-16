# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0002_auto_20150116_1523'),
        ('user', '0003_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='area',
            field=models.ForeignKey(to='location.Area', default=1),
            preserve_default=True,
        ),
    ]
