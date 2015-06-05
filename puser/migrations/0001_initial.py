# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import image_cropping.fields
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('location', '0003_auto_20150421_1424'),
    ]

    operations = [
        migrations.CreateModel(
            name='Info',
            fields=[
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, serialize=False, primary_key=True)),
                ('address', models.CharField(max_length=200, blank=True)),
                ('phone', localflavor.us.models.PhoneNumberField(max_length=20, blank=True)),
                ('note', models.TextField(blank=True)),
                ('picture_original', image_cropping.fields.ImageCropField(upload_to='picture', blank=True, null=True)),
                ('picture_cropping', image_cropping.fields.ImageRatioField('picture_original', '200x200', adapt_rotation=False, size_warning=True, free_crop=False, help_text=None, allow_fullsize=False, verbose_name='picture cropping', hide_image_field=False)),
                ('area', models.ForeignKey(to='location.Area')),
            ],
        ),
    ]
