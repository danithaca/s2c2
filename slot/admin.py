from django.contrib import admin
from slot.models import OfferDateslot, OfferWeekslot, NeedWeekslot, NeedDateslot, MeetDateslot, MeetWeekslot

_weekslot_display = ('start_dow', 'start_time', 'end_dow', 'end_time')
_dateslot_display = ('start_date', 'start_time', 'end_date', 'end_time')
_need_display = ('location',)
_offer_display = ('user', )


class NeedWeekslotAdmin(admin.ModelAdmin):
    list_display = _need_display + _weekslot_display


class NeedDateslotAdmin(admin.ModelAdmin):
    list_display = _need_display + _dateslot_display


class OfferWeekslotAdmin(admin.ModelAdmin):
    list_display = _offer_display + _weekslot_display


class OfferDateslotAdmin(admin.ModelAdmin):
    list_display = _offer_display + _dateslot_display


admin.site.register(NeedWeekslot, NeedWeekslotAdmin)
admin.site.register(OfferWeekslot, OfferWeekslotAdmin)
admin.site.register(MeetWeekslot)
admin.site.register(NeedDateslot, NeedDateslotAdmin)
admin.site.register(OfferDateslot, OfferDateslotAdmin)
admin.site.register(MeetDateslot)