# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'inactive'), (1, 'active'), (20, 'backup')], default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
