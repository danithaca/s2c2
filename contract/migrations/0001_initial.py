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
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('event_start', models.DateTimeField()),
                ('event_end', models.DateTimeField()),
                ('price', models.DecimalField(max_digits=5, decimal_places=2)),
                ('description', models.TextField(blank=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Initiated'), (2, 'Active'), (3, 'Confirmed'), (4, 'Finished'), (5, 'Canceled')], default=1)),
                ('area', models.ForeignKey(to='puser.Area')),
                ('buyer', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='buyer')),
                ('seller', models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL, related_name='seller')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Initialized'), (2, 'Engaged'), (3, 'Declined'), (4, 'Accepted'), (5, 'Canceled')], default=1)),
                ('score', models.FloatField(default=0.0)),
                ('circles', models.ManyToManyField(to='circle.Circle')),
                ('contract', models.ForeignKey(to='contract.Contract')),
                ('target', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='match',
            unique_together=set([('contract', 'target')]),
        ),
        migrations.RenameField(
            model_name='match',
            old_name='target',
            new_name='target_user',
        ),
        migrations.AlterUniqueTogether(
            name='match',
            unique_together=set([('contract', 'target_user')]),
        ),
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
            field=models.OneToOneField(blank=True, null=True, to='contract.Match', related_name='confirmed_contract'),
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
        migrations.AddField(
            model_name='match',
            name='response',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='contract',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Initiated'), (2, 'Active'), (3, 'Confirmed'), (4, 'Successful'), (5, 'Canceled'), (6, 'Failed'), (7, 'Expired')], default=1),
        ),
        migrations.AddField(
            model_name='contract',
            name='audience_data',
            field=models.TextField(help_text='Extra data for the particular audience type, stored in JSON.', blank=True),
        ),
        migrations.AddField(
            model_name='contract',
            name='audience_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Smart'), (2, 'Circle')], default=1),
        ),
        migrations.AddField(
            model_name='contract',
            name='reversed',
            field=models.BooleanField(default=False),
        ),
    ]
