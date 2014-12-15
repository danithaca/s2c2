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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=200)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('location_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='location.Location')),
            ],
            options={
            },
            bases=('location.location',),
        ),
        migrations.CreateModel(
            name='Center',
            fields=[
                ('location_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='location.Location')),
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
