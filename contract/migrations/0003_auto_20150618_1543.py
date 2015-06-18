# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contract', '0002_auto_20150616_0904'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='buyer',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='seller',
        ),
        migrations.AddField(
            model_name='contract',
            name='confirmed_match',
            field=models.OneToOneField(null=True, to='contract.Match', related_name='confirmed_contract', blank=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='initiate_user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contract',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Initiated'), (2, 'Active'), (3, 'Confirmed'), (4, 'Successful'), (5, 'Canceled'), (6, 'Failed')], default=1),
        ),
    ]
