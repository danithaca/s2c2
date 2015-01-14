# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slot', '0002_auto_20150113_1318'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meetdate',
            name='need',
        ),
        migrations.RemoveField(
            model_name='meetdate',
            name='offer',
        ),
        migrations.DeleteModel(
            name='MeetDate',
        ),
        migrations.RemoveField(
            model_name='meetregular',
            name='need',
        ),
        migrations.RemoveField(
            model_name='meetregular',
            name='offer',
        ),
        migrations.DeleteModel(
            name='MeetRegular',
        ),
        migrations.RemoveField(
            model_name='needdate',
            name='location',
        ),
        migrations.DeleteModel(
            name='NeedDate',
        ),
        migrations.RemoveField(
            model_name='needregular',
            name='location',
        ),
        migrations.DeleteModel(
            name='NeedRegular',
        ),
        migrations.RemoveField(
            model_name='offerdate',
            name='user',
        ),
        migrations.DeleteModel(
            name='OfferDate',
        ),
        migrations.RemoveField(
            model_name='offerregular',
            name='user',
        ),
        migrations.DeleteModel(
            name='OfferRegular',
        ),
    ]
