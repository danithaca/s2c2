# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slot', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meet',
            name='id',
        ),
        migrations.AlterField(
            model_name='meet',
            name='need',
            field=models.OneToOneField(primary_key=True, to='slot.NeedSlot'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='meet',
            name='offer',
            field=models.OneToOneField(serialize=False, primary_key=True, to='slot.OfferSlot'),
            preserve_default=True,
        ),
    ]
