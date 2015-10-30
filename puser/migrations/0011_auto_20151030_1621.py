# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('puser', '0010_menuitem_importance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='importance',
            field=models.SmallIntegerField(choices=[(0, 'Regular'), (1, 'Highlight'), (-1, 'Muted')], default=0, help_text='The importance of this item'),
        ),
    ]
