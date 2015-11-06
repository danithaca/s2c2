# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_cropping.fields
from django.conf import settings
import localflavor.us.models
import django.contrib.auth.models
import sitetree.models


class Migration(migrations.Migration):

    dependencies = [
        ('sitetree', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('state', localflavor.us.models.USStateField(max_length=2, choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AS', 'American Samoa'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('AA', 'Armed Forces Americas'), ('AE', 'Armed Forces Europe'), ('AP', 'Armed Forces Pacific'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'), ('FL', 'Florida'), ('GA', 'Georgia'), ('GU', 'Guam'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('MP', 'Northern Mariana Islands'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('PR', 'Puerto Rico'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VI', 'Virgin Islands'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')])),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'location_area',
            },
        ),
        migrations.CreateModel(
            name='Info',
            fields=[
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, serialize=False, primary_key=True)),
                ('address', models.CharField(max_length=200, blank=True)),
                ('phone', localflavor.us.models.PhoneNumberField(max_length=20, blank=True)),
                ('note', models.TextField(blank=True)),
                ('picture_original', image_cropping.fields.ImageCropField(upload_to='picture', blank=True, null=True)),
                ('picture_cropping', image_cropping.fields.ImageRatioField('picture_original', '200x200', allow_fullsize=False, help_text=None, adapt_rotation=False, free_crop=False, verbose_name='picture cropping', size_warning=True, hide_image_field=False)),
                ('area', models.ForeignKey(default=1, to='puser.Area')),
                ('homepage', models.URLField(blank=True)),
                ('role', models.PositiveSmallIntegerField(choices=[(7, 'Parent'), (8, 'Sitter')], blank=True, null=True)),
                ('phone_backup', localflavor.us.models.PhoneNumberField(help_text='Phone number added by other people', blank=True, max_length=20)),
                ('registered', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='PUser',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterModelTable(
            name='area',
            table=None,
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(verbose_name='Title', help_text='Site tree item title. Can contain template variables E.g.: {{ mytitle }}.', max_length=100)),
                ('hint', models.CharField(verbose_name='Hint', help_text='Some additional information about this item that is used as a hint.', blank=True, max_length=200, default='')),
                ('url', models.CharField(db_index=True, verbose_name='URL', help_text='Exact URL or URL pattern (see "Additional settings") for this item.', max_length=200)),
                ('urlaspattern', models.BooleanField(db_index=True, verbose_name='URL as Pattern', help_text='Whether the given URL should be treated as a pattern.<br /><b>Note:</b> Refer to Django "URL dispatcher" documentation (e.g. "Naming URL patterns" part).', default=False)),
                ('hidden', models.BooleanField(db_index=True, verbose_name='Hidden', help_text='Whether to show this item in navigation.', default=False)),
                ('alias', sitetree.models.CharFieldNullable(help_text='Short name to address site tree item from a template.<br /><b>Reserved aliases:</b> "trunk", "this-children", "this-siblings", "this-ancestor-children", "this-parent-siblings".', blank=True, null=True, db_index=True, verbose_name='Alias', max_length=80)),
                ('description', models.TextField(verbose_name='Description', help_text='Additional comments on this item.', blank=True, default='')),
                ('inmenu', models.BooleanField(db_index=True, verbose_name='Show in menu', help_text='Whether to show this item in a menu.', default=True)),
                ('inbreadcrumbs', models.BooleanField(db_index=True, verbose_name='Show in breadcrumb path', help_text='Whether to show this item in a breadcrumb path.', default=True)),
                ('insitetree', models.BooleanField(db_index=True, verbose_name='Show in site tree', help_text='Whether to show this item in a site tree.', default=True)),
                ('access_loggedin', models.BooleanField(db_index=True, verbose_name='Logged in only', help_text='Check it to grant access to this item to authenticated users only.', default=False)),
                ('access_guest', models.BooleanField(db_index=True, verbose_name='Guests only', help_text='Check it to grant access to this item to guests only.', default=False)),
                ('access_restricted', models.BooleanField(db_index=True, verbose_name='Restrict access to permissions', help_text='Check it to restrict user access to this item, using Django permissions system.', default=False)),
                ('access_perm_type', models.IntegerField(verbose_name='Permissions interpretation', help_text='<b>Any</b> &mdash; user should have any of chosen permissions. <b>All</b> &mdash; user should have all chosen permissions.', choices=[(1, 'Any'), (2, 'All')], default=1)),
                ('sort_order', models.IntegerField(db_index=True, verbose_name='Sort order', help_text='Item position among other site tree items under the same parent.', default=0)),
                ('fa_icon', models.CharField(help_text='Font awesome icon', blank=True, max_length=50)),
                ('css_id', models.CharField(help_text='CSS ID', blank=True, max_length=50)),
                ('access_permissions', models.ManyToManyField(verbose_name='Permissions granting access', blank=True, to='auth.Permission')),
                ('parent', models.ForeignKey(help_text='Parent site tree item.', blank=True, null=True, to='puser.MenuItem', verbose_name='Parent', related_name='menuitem_parent')),
                ('tree', models.ForeignKey(help_text='Site tree this item belongs to.', to='sitetree.Tree', verbose_name='Site Tree', related_name='menuitem_tree')),
            ],
            options={
                'verbose_name': 'Site Tree Item',
                'abstract': False,
                'verbose_name_plural': 'Site Tree Items',
            },
        ),
        migrations.AlterUniqueTogether(
            name='menuitem',
            unique_together=set([('tree', 'alias')]),
        ),
        migrations.RemoveField(
            model_name='menuitem',
            name='css_id',
        ),
        migrations.AddField(
            model_name='menuitem',
            name='importance',
            field=models.SmallIntegerField(default=0, help_text='The importance of this item', choices=[(0, 'Regular'), (1, 'Highlight'), (-1, 'Muted')]),
        ),
        migrations.CreateModel(
            name='Waiting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(default=None, blank=True, null=True, to='puser.PUser')),
            ],
        ),
    ]
