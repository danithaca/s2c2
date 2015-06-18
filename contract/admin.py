from django.contrib import admin
from contract import models

@admin.register(models.Contract)
class CircleAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'seller', 'event_start', 'event_end', 'price', 'description', 'status', 'area')\

@admin.register(models.Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'target_user', 'status')