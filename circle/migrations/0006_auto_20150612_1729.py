# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0005_auto_20150612_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('member', 'circle')]),
        ),
    ]
