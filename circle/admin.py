from django.contrib import admin
from circle import models


@admin.register(models.Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'owner', 'area')


@admin.register(models.SupersetRel)
class SupersetAdmin(admin.ModelAdmin):
    list_display = ('child', 'parent', 'created')


@admin.register(models.Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('member', 'circle', 'active', 'approved', 'type')
