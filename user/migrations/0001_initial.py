# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models
import image_cropping.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(serialize=False, primary_key=True, to=settings.AUTH_USER_MODEL)),
                ('address', models.CharField(blank=True, max_length=200)),
                ('phone_main', localflavor.us.models.PhoneNumberField(blank=True, max_length=20)),
                ('phone_backup', localflavor.us.models.PhoneNumberField(blank=True, max_length=20)),
                ('verified', models.NullBooleanField()),
                ('centers', models.ManyToManyField(blank=True, to='location.Center')),
                ('note', models.TextField(blank=True, null=True)),
                ('area', models.ForeignKey(to='location.Area', default=1)),
                ('picture_cropping', image_cropping.fields.ImageRatioField('picture_original', '200x200', verbose_name='picture cropping', size_warning=True, free_crop=False, adapt_rotation=False, allow_fullsize=False, hide_image_field=False, help_text=None)),
                ('picture_original', image_cropping.fields.ImageCropField(blank=True, null=True, upload_to='picture')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('group', models.OneToOneField(serialize=False, primary_key=True, to='auth.Group')),
                ('machine_name', models.SlugField()),
                ('type_center', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
