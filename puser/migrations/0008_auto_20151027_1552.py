# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sitetree.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('sitetree', '0001_initial'),
        ('puser', '0007_info_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Site tree item title. Can contain template variables E.g.: {{ mytitle }}.', max_length=100, verbose_name='Title')),
                ('hint', models.CharField(help_text='Some additional information about this item that is used as a hint.', max_length=200, default='', blank=True, verbose_name='Hint')),
                ('url', models.CharField(help_text='Exact URL or URL pattern (see "Additional settings") for this item.', max_length=200, db_index=True, verbose_name='URL')),
                ('urlaspattern', models.BooleanField(db_index=True, help_text='Whether the given URL should be treated as a pattern.<br /><b>Note:</b> Refer to Django "URL dispatcher" documentation (e.g. "Naming URL patterns" part).', default=False, verbose_name='URL as Pattern')),
                ('hidden', models.BooleanField(db_index=True, help_text='Whether to show this item in navigation.', default=False, verbose_name='Hidden')),
                ('alias', sitetree.models.CharFieldNullable(blank=True, verbose_name='Alias', help_text='Short name to address site tree item from a template.<br /><b>Reserved aliases:</b> "trunk", "this-children", "this-siblings", "this-ancestor-children", "this-parent-siblings".', max_length=80, db_index=True, null=True)),
                ('description', models.TextField(help_text='Additional comments on this item.', default='', blank=True, verbose_name='Description')),
                ('inmenu', models.BooleanField(db_index=True, help_text='Whether to show this item in a menu.', default=True, verbose_name='Show in menu')),
                ('inbreadcrumbs', models.BooleanField(db_index=True, help_text='Whether to show this item in a breadcrumb path.', default=True, verbose_name='Show in breadcrumb path')),
                ('insitetree', models.BooleanField(db_index=True, help_text='Whether to show this item in a site tree.', default=True, verbose_name='Show in site tree')),
                ('access_loggedin', models.BooleanField(db_index=True, help_text='Check it to grant access to this item to authenticated users only.', default=False, verbose_name='Logged in only')),
                ('access_guest', models.BooleanField(db_index=True, help_text='Check it to grant access to this item to guests only.', default=False, verbose_name='Guests only')),
                ('access_restricted', models.BooleanField(db_index=True, help_text='Check it to restrict user access to this item, using Django permissions system.', default=False, verbose_name='Restrict access to permissions')),
                ('access_perm_type', models.IntegerField(help_text='<b>Any</b> &mdash; user should have any of chosen permissions. <b>All</b> &mdash; user should have all chosen permissions.', choices=[(1, 'Any'), (2, 'All')], default=1, verbose_name='Permissions interpretation')),
                ('sort_order', models.IntegerField(db_index=True, help_text='Item position among other site tree items under the same parent.', default=0, verbose_name='Sort order')),
                ('fa_icon', models.CharField(help_text='Font awesome icon', blank=True, max_length=50)),
                ('css_id', models.CharField(help_text='CSS ID', blank=True, max_length=50)),
                ('access_permissions', models.ManyToManyField(to='auth.Permission', blank=True, verbose_name='Permissions granting access')),
                ('parent', models.ForeignKey(blank=True, verbose_name='Parent', to='puser.MenuItem', related_name='menuitem_parent', help_text='Parent site tree item.', null=True)),
                ('tree', models.ForeignKey(verbose_name='Site Tree', related_name='menuitem_tree', help_text='Site tree this item belongs to.', to='sitetree.Tree')),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'Site Tree Items',
                'verbose_name': 'Site Tree Item',
            },
        ),
        migrations.AlterUniqueTogether(
            name='menuitem',
            unique_together=set([('tree', 'alias')]),
        ),
    ]
