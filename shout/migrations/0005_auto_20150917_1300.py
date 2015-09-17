# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shout', '0004_auto_20150630_1130'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shout',
            old_name='audience',
            new_name='audience_type',
        ),
        migrations.AlterField(
            model_name='shout',
            name='subject',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
