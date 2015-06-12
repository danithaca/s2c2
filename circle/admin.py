from django.contrib import admin
from circle import models


@admin.register(models.Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'owner', 'area')


@admin.register(models.Superset)
class SupersetAdmin(admin.ModelAdmin):
    list_display = ('child', 'parent', 'created')