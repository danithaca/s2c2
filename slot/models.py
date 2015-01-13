from itertools import product
import warnings
from django.db import models
from django.contrib.auth.models import User
from location.models import Location
import calendar
from datetime import time, timedelta, datetime, date


class Day(object):
    # this is a combined field.
    # if it's a day-of-week, it'll be 1900-1-1 (which is a monday)
    # if it's a date, it'll be yyyymmdd
    def __init__(self, value):
        assert (0 <= value <= 6) or (100101 <= value <= 991230)
        self.value = value


class Slot(models.Model):
    """
    Any class that has the start_time and end_time will be subclass of this.
    """
    start_time = models.TimeField()
    end_time = models.TimeField()

    start_day = models.IntegerField()

    class Meta():
        abstract = True


class OfferSlot(Slot):
    user = models.ForeignKey(User)


class NeedSlot(Slot):
    location = models.ForeignKey(Location)


class MeetSlot(Slot):
    offer = models.ForeignKey(OfferSlot)
    need = models.ForeignKey(NeedSlot)

    INACTIVE = 0
    MAIN = 1      # only 1 meet could be "active" that associate the same "offer" and "need".
    BACKUP = 20
    MEET_STATUS = (
        (INACTIVE, 'inactive'),
        (MAIN, 'main'),
        (BACKUP, 'backup'),
    )
    status = models.PositiveSmallIntegerField(choices=MEET_STATUS, default=INACTIVE)


# ---------------------- Below are old code.--------------------------------------------


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


class SlotOld(models.Model):
    """
    Any class that has the start_time and end_time will be subclass of this.
    """
    start_time = models.TimeField()
    end_time = models.TimeField()

    def get_start_time_display(self):
        return HalfHourTime.display(self.start_time)

    def get_end_time_display(self):
        return HalfHourTime.display(self.end_time)

    class Meta():
        abstract = True


class RegularSlot(SlotOld):
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


class DateSlot(SlotOld):
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
    :deprecated::
    """
    warnings.warn("Deprecated in favor of OfferSlot", DeprecationWarning)

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
        deleted_time = []
        for st in HalfHourTime.interval(start_time, end_time):
            h = HalfHourTime(st)
            queryset = OfferRegular.objects.filter(start_dow=start_dow, user=user, start_time=h.start_time, end_time=h.end_time)
            if not queryset.exists():
                continue
            queryset.delete()
            deleted_time.append(h.start_time)
        return deleted_time

    @staticmethod
    def delete_all(start_dow, user):
        queryset = OfferRegular.objects.filter(start_dow=start_dow, user=user)
        if queryset.exists():
            queryset.delete()
            return True
        else:
            return False

    @staticmethod
    def get_staff_id_list(start_dow, start_time):
        # fixme: need to support "center" relationship too.
        return OfferRegular.objects\
            .filter(start_dow=start_dow, start_time=start_time, end_time=HalfHourTime.next(start_time)) \
            .exclude(meetregular__status=MeetInfo.MAIN)\
            .values_list('user_id', flat=True).distinct()

    def __str__(self):
        self.get_start_dow_display()
        return '%s: %s %s ~ %s' % (self.user.username, self.get_start_dow_display(), self.get_start_time_display(), self.get_end_time_display())


class OfferDate(OfferInfo, DateSlot):
    """
    Real class for offer on particular date.
    """
    pass


class NeedRegular(NeedInfo, RegularSlot):
    """
    Real class for offer on particular date.
    """
    @staticmethod
    def add_interval(start_dow, location, start_time, end_time, howmany=1):
        """ Add needs regardless of whether the needs exists already """
        for st in HalfHourTime.interval(start_time, end_time):
            h = HalfHourTime(st)
            for i in range(howmany):
                m = NeedRegular(start_dow=start_dow, location=location, start_time=h.start_time, end_time=h.end_time)
                m.save()

    def __str__(self):
        return '%s: %s %s ~ %s' % (self.location.name, self.get_start_dow_display(), self.start_time, self.end_time)


class NeedDate(NeedInfo, DateSlot):
    """
    Real class for need on particular date.
    """
    pass


class MeetInfo(models.Model):
    INACTIVE = 0
    MAIN = 1      # only 1 meet could be "active" that associate the same "offer" and "need".
    BACKUP = 20
    MEET_STATUS = (
        (INACTIVE, 'inactive'),
        (MAIN, 'main'),
        (BACKUP, 'backup'),
    )
    status = models.PositiveSmallIntegerField(choices=MEET_STATUS, default=INACTIVE)

    class Meta():
        abstract = True


class MeetRegular(MeetInfo, RegularSlot):
    """
    Class that associate an offer with a need.
    Start/end time must match exactly. Or else need to break up big chunk into smaller chunks.
    """
    offer = models.ForeignKey(OfferRegular)
    need = models.ForeignKey(NeedRegular)


class MeetDate(MeetInfo, DateSlot):
    offer = models.ForeignKey(OfferDate)
    need = models.ForeignKey(NeedDate)