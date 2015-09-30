# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('circle', '0004_superset'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='circle.Membership'),
        ),
        migrations.AlterField(
            model_name='circle',
            name='area',
            field=models.ForeignKey(default=1, to='puser.Area'),
        ),
        migrations.AlterField(
            model_name='circle',
            name='owner',
            field=models.ForeignKey(related_name='owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='superset',
            unique_together=set([('child', 'parent')]),
        ),
    ]
