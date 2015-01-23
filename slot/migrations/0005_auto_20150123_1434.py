# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slot', '0004_auto_20150122_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meet',
            name='offer',
            field=models.OneToOneField(primary_key=True, to='slot.OfferSlot'),
            preserve_default=True,
        ),
    ]
