# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circle', '0006_auto_20150612_1729'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupersetRel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('child', models.ForeignKey(related_name='child', to='circle.Circle')),
                ('parent', models.ForeignKey(related_name='parent', to='circle.Circle')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='superset',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='superset',
            name='child',
        ),
        migrations.RemoveField(
            model_name='superset',
            name='parent',
        ),
        migrations.DeleteModel(
            name='Superset',
        ),
        migrations.AlterUniqueTogether(
            name='supersetrel',
            unique_together=set([('child', 'parent')]),
        ),
    ]
