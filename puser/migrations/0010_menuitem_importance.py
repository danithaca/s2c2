# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('puser', '0009_remove_menuitem_css_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='importance',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Regular'), (1, 'Highlight'), (-1, 'Muted')], help_text='The importance of this item'),
        ),
    ]
