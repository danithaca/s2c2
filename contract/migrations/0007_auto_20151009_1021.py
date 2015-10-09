# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0006_auto_20150916_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='initiate_user',
            field=models.ForeignKey(to='puser.PUser'),
        ),
        migrations.AlterField(
            model_name='match',
            name='target_user',
            field=models.ForeignKey(to='puser.PUser'),
        ),
    ]
