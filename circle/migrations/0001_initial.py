# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('puser', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Circle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Personal'), (2, 'Public'), (3, 'Agency')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('area', models.ForeignKey(to='puser.Area')),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('active', models.BooleanField(default=False)),
                ('type', models.PositiveSmallIntegerField(default=1, choices=[(1, 'Normal'), (2, 'Admin')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('circle', models.ForeignKey(to='circle.Circle')),
                ('member', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('approved', models.BooleanField(default=False)),
            ],
        ),
        migrations.RenameField(
            model_name='circle',
            old_name='creator',
            new_name='owner',
        ),
        migrations.AlterField(
            model_name='circle',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Personal'), (2, 'Public'), (3, 'Agency'), (4, 'Superset')]),
        ),
        migrations.CreateModel(
            name='Superset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('child', models.ForeignKey(to='circle.Circle', related_name='child')),
                ('parent', models.ForeignKey(to='circle.Circle', related_name='parent')),
            ],
        ),
        migrations.AddField(
            model_name='circle',
            name='members',
            field=models.ManyToManyField(through='circle.Membership', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='circle',
            name='area',
            field=models.ForeignKey(to='puser.Area', default=1),
        ),
        migrations.AlterField(
            model_name='circle',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='owner'),
        ),
        migrations.AlterUniqueTogether(
            name='superset',
            unique_together=set([('child', 'parent')]),
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('member', 'circle')]),
        ),
        migrations.CreateModel(
            name='SupersetRel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('child', models.ForeignKey(to='circle.Circle', related_name='child')),
                ('parent', models.ForeignKey(to='circle.Circle', related_name='parent')),
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
        migrations.AlterField(
            model_name='membership',
            name='approved',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AddField(
            model_name='circle',
            name='homepage',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='membership',
            name='type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'Normal'), (2, 'Admin'), (3, 'Partial'), (4, 'Homo')]),
        ),
        migrations.AlterField(
            model_name='circle',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Personal'), (2, 'Public'), (3, 'Agency'), (4, 'Superset'), (7, 'Parent'), (8, 'Babysitter'), (9, 'Tag')]),
        ),
        migrations.AlterField(
            model_name='circle',
            name='area',
            field=models.ForeignKey(to='puser.Area'),
        ),
        migrations.CreateModel(
            name='ParentCircle',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('circle.circle',),
        ),
        migrations.AlterField(
            model_name='circle',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Personal'), (2, 'Public'), (3, 'Agency'), (4, 'Superset'), (7, 'Parent'), (8, 'Sitter'), (9, 'Tag')]),
        ),
        migrations.AddField(
            model_name='membership',
            name='note',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='membership',
            name='type',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, 'Normal'), (2, 'Admin'), (3, 'Partial'), (4, 'Favorite')]),
        ),
    ]
