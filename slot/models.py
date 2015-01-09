from itertools import product
from django.db import models
from django.contrib.auth.models import User
from location.models import Location
import calendar
from datetime import time, timedelta, datetime, date


class DayOfWeek(object):
    @staticmethod
    def get_tuple():
        return (calendar.MONDAY, calendar.TUESDAY, calendar.WEDNESDAY, calendar.THURSDAY, calendar.FRIDAY, calendar.SATURDAY, calendar.SUNDAY)

    @staticmethod
    def get_choices():
        return tuple((d, calendar.day_name[d]) for d in DayOfWeek.get_tuple())

    @staticmethod
    def get_set():
        return set(DayOfWeek.get_tuple())

    @staticmethod
    def get_name(dow):
        return calendar.day_name[dow]

    def __init__(self, dow):
        assert dow in DayOfWeek.get_set()
        self.dow = dow

    def prev(self):
        return DayOfWeek(DayOfWeek.get_tuple()[self.dow - 1])

    def next(self):
        return DayOfWeek(DayOfWeek.get_tuple()[(self.dow + 1) % 7])

    @property
    def name(self):
        return DayOfWeek.get_name(self.dow)


class HalfHourTime(object):
    """
    helper class for handling slot based on half hour interval
    """
    tuple = tuple(sorted(time(hour=h, minute=m) for h, m in product(range(24), (0, 30))))
    set = set(time(hour=h, minute=m) for h, m in product(range(24), (0, 30)))
    map = {t: i for i, t in enumerate(tuple)}
    strformat = '%I:%M%p'

    @staticmethod
    def next(t):
        assert t in HalfHourTime.set
        return HalfHourTime.tuple[(HalfHourTime.map[t] + 1) % len(HalfHourTime.tuple)]

    @staticmethod
    def prev(t):
        assert t in HalfHourTime.set
        return HalfHourTime.tuple[(HalfHourTime.map[t] - 1)]

    @staticmethod
    def interval(start_time, end_time):
        # this is end-exclusive [start, end)
        assert start_time in HalfHourTime.set and end_time in HalfHourTime.set and end_time > start_time
        return HalfHourTime.tuple[HalfHourTime.map[start_time]:HalfHourTime.map[end_time]]

    @staticmethod
    def display(t):
        return t.strftime(HalfHourTime.strformat)

    @staticmethod
    def parse(s):
        t = datetime.strptime(s, HalfHourTime.strformat).time()
        assert t in HalfHourTime.set
        return t

    @staticmethod
    def get_choices(start_time, end_time):
        return tuple([(HalfHourTime.display(t), HalfHourTime.display(t)) for t in HalfHourTime.interval(start_time, end_time)])

    def __init__(self, start_time):
        assert start_time in HalfHourTime.set
        self.start_time = start_time
        self.end_time = HalfHourTime.next(self.start_time)

    def __str__(self):
        return '%s ~ %s' % (HalfHourTime.display(self.start_time), HalfHourTime.display(self.end_time))


class Slot(models.Model):
    """
    Any class that has the start_time and end_time will be subclass of this.
    """
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta():
        abstract = True


class RegularSlot(Slot):
    # todo: use python calendar.MONDAY, calendar.day_name[0] and calendar.iterweekdays() instead.
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

    DAY_OF_WEEK_SET = set([t[0] for t in DAY_OF_WEEK])

    start_dow = models.PositiveSmallIntegerField(choices=DAY_OF_WEEK)
    # end_dow = models.PositiveSmallIntegerField(choices=DAY_OF_WEEK, blank=True, null=True)

    class Meta():
        abstract = True


class DateSlot(Slot):
    start_date = models.DateField()
    # end_date = models.DateField(blank=True, null=True)

    class Meta():
        abstract = True


class OfferInfo(models.Model):
    user = models.ForeignKey(User)

    class Meta():
        abstract = True


class NeedInfo(models.Model):
    location = models.ForeignKey(Location)

    class Meta():
        abstract = True


class OfferRegular(OfferInfo, RegularSlot):
    """
    Real class for offer on the regular schedule
    """
    @staticmethod
    def add_interval(start_dow, user, start_time, end_time):
        added_time = []
        for st in HalfHourTime.interval(start_time, end_time):
            h = HalfHourTime(st)
            if OfferRegular.objects.filter(start_dow=start_dow, user=user, start_time=h.start_time, end_time=h.end_time).exists():
                continue
            m = OfferRegular(start_dow=start_dow, user=user, start_time=h.start_time, end_time=h.end_time)
            m.save()
            added_time.append(h.start_time)
        return added_time

    @staticmethod
    def delete_interval(start_dow, user, start_time, end_time):
        for st in HalfHourTime.interval(start_time, end_time):
            h = HalfHourTime(st)
            OfferRegular.objects.filter(start_dow=start_dow, user=user, start_time=h.start_time, end_time=h.end_time).delete()


class OfferDate(OfferInfo, DateSlot):
    """
    Real class for offer on particular date.
    """
    pass


class NeedRegular(NeedInfo, RegularSlot):
    """
    Real class for offer on particular date.
    """
    pass


class NeedDate(NeedInfo, DateSlot):
    """
    Real class for need on particular date.
    """
    pass


class MeetInfo(models.Model):
    INACTIVE = 0
    ACTIVE = 1      # only 1 meet could be "active" that associate the same "offer" and "need".
    BACKUP = 20
    MEET_STATUS = (
        (INACTIVE, 'inactive'),
        (ACTIVE, 'active'),
        (BACKUP, 'backup'),
    )
    status = models.PositiveSmallIntegerField(choices=MEET_STATUS, default=INACTIVE)


class MeetRegular(RegularSlot):
    """
    Class that associate an offer with a need.
    Start/end time must match exactly. Or else need to break up big chunk into smaller chunks.
    """
    offer = models.ForeignKey(OfferRegular)
    need = models.ForeignKey(NeedRegular)


class MeetDate(DateSlot):
    offer = models.ForeignKey(OfferDate)
    need = models.ForeignKey(NeedDate)