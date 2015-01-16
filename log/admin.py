from django.contrib import admin

from log import models


admin.site.register(models.Log)
admin.site.register(models.Notification)