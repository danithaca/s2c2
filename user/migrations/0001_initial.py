# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0003_auto_20141215_2051'),
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('address', models.CharField(max_length=200, blank=True)),
                ('phone_main', models.CharField(max_length=12)),
                ('phone_backup', models.CharField(max_length=12, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('group_ptr', models.OneToOneField(primary_key=True, to='auth.Group', serialize=False, auto_created=True, parent_link=True)),
                ('title', models.CharField(max_length=50)),
                ('function_center', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=('auth.group',),
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('profile_ptr', models.OneToOneField(primary_key=True, to='user.Profile', serialize=False, auto_created=True, parent_link=True)),
                ('role', models.PositiveSmallIntegerField(choices=[(1, 'Director'), (2, 'Teacher'), (3, 'NC Support'), (4, 'Student Intern')])),
                ('checked', models.BooleanField(default=False)),
                ('centers', models.ManyToManyField(to='location.Center')),
            ],
            options={
            },
            bases=('user.profile',),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
        ),
    ]
