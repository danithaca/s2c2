# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_auto_20150122_1313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='picture',
        ),
        migrations.AddField(
            model_name='profile',
            name='picture_cropping',
            field=image_cropping.fields.ImageRatioField('picture_original', '200x200', size_warning=True, help_text=None, hide_image_field=False, verbose_name='picture cropping', free_crop=False, adapt_rotation=False, allow_fullsize=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='picture_original',
            field=image_cropping.fields.ImageCropField(null=True, upload_to='picture', blank=True),
            preserve_default=True,
        ),
    ]
