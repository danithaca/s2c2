# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0003_auto_20150611_1603'),
    ]

    operations = [
        migrations.CreateModel(
            name='Superset',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('child', models.ForeignKey(related_name='child', to='circle.Circle')),
                ('parent', models.ForeignKey(related_name='parent', to='circle.Circle')),
            ],
        ),
    ]
