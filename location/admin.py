from django.contrib import admin

from location import models


@admin.register(models.Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', )


@admin.register(models.Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'area', 'status')


@admin.register(models.Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'center')

admin.site.register(models.Neverland)