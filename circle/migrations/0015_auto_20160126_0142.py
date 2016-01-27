# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0014_membership_private_note'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membership',
            name='rel_colleague',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='rel_direct_family',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='rel_extended_family',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='rel_friend',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='rel_kid_friend',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='rel_neighbor',
        ),
        migrations.AddField(
            model_name='membership',
            name='as_rel',
            field=models.CommaSeparatedIntegerField(max_length=100, blank=True, default=''),
        ),
    ]
