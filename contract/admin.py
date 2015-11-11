from django.contrib import admin

from contract import models


@admin.register(models.Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'initiate_user', 'event_start', 'event_end', 'price', 'description', 'status', 'area')

@admin.register(models.Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'target_user', 'status')