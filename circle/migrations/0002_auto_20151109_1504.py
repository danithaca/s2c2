# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle',
            name='config',
            field=models.TextField(help_text='JSON field for special settings.', blank=True),
        ),
        migrations.AddField(
            model_name='membership',
            name='as_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='membership',
            name='as_parent',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='membership',
            name='as_sitter',
            field=models.BooleanField(default=False),
        ),
    ]
