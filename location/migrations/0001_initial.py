# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('address', models.CharField(blank=True, max_length=200)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('location_ptr', models.OneToOneField(serialize=False, auto_created=True, parent_link=True, to='location.Location', primary_key=True)),
            ],
            options={
            },
            bases=('location.location',),
        ),
        migrations.CreateModel(
            name='Center',
            fields=[
                ('location_ptr', models.OneToOneField(serialize=False, auto_created=True, parent_link=True, to='location.Location', primary_key=True)),
            ],
            options={
            },
            bases=('location.location',),
        ),
        migrations.AddField(
            model_name='location',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='classroom',
            name='center',
            field=models.ForeignKey(to='location.Center'),
            preserve_default=True,
        ),
    ]
