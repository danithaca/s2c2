# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='match',
            old_name='target',
            new_name='target_user',
        ),
        migrations.AlterUniqueTogether(
            name='match',
            unique_together=set([('contract', 'target_user')]),
        ),
    ]
