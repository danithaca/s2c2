from django.db import models
from django.contrib.auth.models import User
from location.models import Location


class SlotMixin(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta():
        abstract = True


class WeekslotMixin(SlotMixin):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    DAY_OF_WEEK = (
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday')
    )

    start_dow = models.PositiveSmallIntegerField(choices=DAY_OF_WEEK)
    end_dow = models.PositiveSmallIntegerField(choices=DAY_OF_WEEK, blank=True, null=True)

    class Meta():
        abstract = True


class DateslotMixin(SlotMixin):
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    class Meta():
        abstract = True


class OfferMixin(models.Model):
    user = models.ForeignKey(User)

    class Meta():
        abstract = True


class NeedMixin(models.Model):
    location = models.ForeignKey(Location)

    class Meta():
        abstract = True


class OfferWeekslot(OfferMixin, WeekslotMixin):
    pass


class OfferDateslot(OfferMixin, DateslotMixin):
    pass


class NeedWeekslot(NeedMixin, WeekslotMixin):
    pass


class NeedDateslot(NeedMixin, DateslotMixin):
    pass


# WeekslotMixin might be redundant?
# The only time it's needed is when offer/need is not completely used up.
class MeetWeekslot(WeekslotMixin):
    offer = models.ForeignKey(OfferWeekslot)
    need = models.ForeignKey(NeedWeekslot)


class MeetDateslot(DateslotMixin):
    offer = models.ForeignKey(OfferDateslot)
    need = models.ForeignKey(NeedDateslot)