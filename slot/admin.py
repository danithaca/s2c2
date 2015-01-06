from django.contrib import admin
from slot.models import OfferDate, OfferRegular, NeedRegular, NeedDate, MeetDate, MeetRegular

_regular_display = ('start_dow', 'start_time', 'end_time')
_date_display = ('start_date', 'start_time', 'end_time')
_need_display = ('location',)
_offer_display = ('user', )


class NeedRegularAdmin(admin.ModelAdmin):
    list_display = _need_display + _regular_display


class NeedDateAdmin(admin.ModelAdmin):
    list_display = _need_display + _date_display


class OfferRegularAdmin(admin.ModelAdmin):
    list_display = _offer_display + _regular_display


class OfferDateAdmin(admin.ModelAdmin):
    list_display = _offer_display + _date_display


class MeetRegularAdmin(admin.ModelAdmin):
    list_display = ('need', 'offer') + _regular_display


class MeetDateAdmin(admin.ModelAdmin):
    list_display = ('need', 'offer') + _date_display


admin.site.register(NeedRegular, NeedRegularAdmin)
admin.site.register(OfferRegular, OfferRegularAdmin)
admin.site.register(MeetRegular, MeetRegularAdmin)
admin.site.register(NeedDate, NeedDateAdmin)
admin.site.register(OfferDate, OfferDateAdmin)
admin.site.register(MeetDate, MeetDateAdmin)