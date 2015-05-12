# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0003_auto_20150421_1424'),
    ]

    operations = [
        migrations.CreateModel(
            name='Neverland',
            fields=[
                ('location_ptr', models.OneToOneField(to='location.Location', parent_link=True, primary_key=True, auto_created=True, serialize=False)),
            ],
            options={
            },
            bases=('location.location',),
        ),
    ]
