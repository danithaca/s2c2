# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0012_membership_as_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membership',
            name='as_type',
        ),
        migrations.AddField(
            model_name='membership',
            name='rel_colleague',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='membership',
            name='rel_direct_family',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='membership',
            name='rel_extended_family',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='membership',
            name='rel_friend',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='membership',
            name='rel_kid_friend',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='membership',
            name='rel_neighbor',
            field=models.BooleanField(default=False),
        ),
    ]
