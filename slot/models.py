from functools import total_ordering
from itertools import product
import warnings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from location.models import Location
import calendar, re
from datetime import time, timedelta, datetime, date


class DayToken(object):
    # if it's a day-of-week, it'll be 1900-1-1 (which is a monday)
    # if it's a date, it'll be yyyymmdd
    # token definition: 0~6 is regular weekday, 20100101~20301230 is specific date.
    # someday: might consider 'date' subclass instead of proxy pattern?

    weekday_tuple = tuple([date(1900, 1, i + 1) for i in range(7)])

    def __init__(self, value):
        assert isinstance(value, date) and DayToken.check_date(value)
        self.value = value

    def is_regular(self):
        return date(1900, 1, 1) <= self.value <= date(1900, 1, 7)

    def get_token(self):
        if self.is_regular():
            return str(self.value.weekday())
        else:
            return self.value.strftime('%Y%m%d')

    @staticmethod
    def check_date(value):
        assert isinstance(value, date)
        return date(1900, 1, 1) <= value <= date(1900, 1, 7) or date(2010, 1, 1) <= value <= date(2030, 1, 1)

    @staticmethod
    def from_token(token):
        assert isinstance(token, str)
        if re.fullmatch('([0-6])|(\d{8})', token) is not None:
            if len(token) == 1:
                return DayToken(date(1900, 1, int(token) + 1))
            else:
                value = datetime.strptime(token, '%Y%m%d').date()
                if not DayToken.check_date(value):
                    raise ValueError('Valid date between 2010-01-01 and 2030-12-31')
                return DayToken(value)
        else:
            raise ValueError('Cannot identify DayToken: %s' % token)

    def __eq__(self, other):
        assert isinstance(other, DayToken)
        return self.value == other.value

    def display_weekday(self):
        return calendar.day_name[self.value.weekday()]

    def weekday(self):
        return self.value.weekday()

    def next_day(self):
        if self.is_regular() and self.value == date(1900, 1, 7):
            return DayToken(date(1900, 1, 1))
        else:
            return DayToken(self.value + timedelta(days=1))

    def prev_day(self):
        if self.is_regular() and self.value == date(1900, 1, 1):
            return DayToken(date(1900, 1, 7))
        else:
            return DayToken(self.value - timedelta(days=1))

    def next_week(self):
        if self.is_regular():
            return self
        else:
            return DayToken(self.value + timedelta(days=7))

    def prev_week(self):
        if self.is_regular():
            return self
        else:
            return DayToken(self.value - timedelta(days=7))

    def expand_week(self):
        if self.is_regular():
            return [DayToken(d) for d in DayToken.weekday_tuple]
        else:
            return [DayToken(self.value - timedelta(days=i)) for i in range(self.weekday(), 0, -1)] + [self, ]\
                   + [DayToken(self.value + timedelta(days=i+1)) for i in range(6 - self.weekday())]

    def __str__(self):
        return str(self.value)


class DayTokenField(models.DateField, metaclass=models.SubfieldBase):
    description = 'Either a regular weekday between 1900-1-1 and 1900-1-7,' \
                  ' or a specific date between 2010-1-1 and 2030-1-1.'

    # no need to override __init__() or deconstruct(). we use the default on for DateField.

    def to_python(self, value):
        try:
            if value is None:
                return None
            if isinstance(value, str):
                # when value is a string, it's a token.
                return DayToken.from_token(value)
            elif isinstance(value, int):
                # when value is int, make it a string and do the same.
                return DayToken.from_token(str(value))
            elif isinstance(value, date):
                # when the value is date, go through the super one, and then return DayToken
                _value = super(DayTokenField, self).to_python(value)
                return DayToken(_value)
            elif isinstance(value, DayToken):
                # if it's just DayToken, don't change anything.
                return value
            else:
                raise ValidationError('Cannot identify DayToken type: %s' % type(value))
        except ValueError as e:
            raise ValidationError(e)

    def get_prep_value(self, value):
        if value is None:
            return None
        assert isinstance(value, DayToken)
        return value.value


@total_ordering
class TimeToken(object):
    # we use the proxy pattern instead of sub-class to avoid weird things.
    # currently only allow half hour time point.

    @staticmethod
    def _to_index(t):
        return t.hour * 2 + t.minute // 30

    @staticmethod
    def _from_index(i):
        return time(i // 2, (i % 2) * 30)

    @staticmethod
    def _next(t):
        return TimeToken._from_index((TimeToken._to_index(t) + 1) % 48)

    @staticmethod
    def _prev(t):
        return TimeToken._from_index((TimeToken._to_index(t) + 47) % 48)

    def __init__(self, value):
        assert isinstance(value, time) and TimeToken.check_time(value)
        self.value = value

    def get_token(self):
        return self.value.strftime('%H%M')

    @staticmethod
    def from_token(token):
        assert isinstance(token, str)
        t = datetime.strptime(token, '%H%M').time()
        if not TimeToken.check_time(t):
            raise ValueError('Current a TimeToken instance has to be at half hour point.')
        return TimeToken(t)

    @staticmethod
    def check_time(value):
        return isinstance(value, time) and value.minute in (0, 30) and value.second == 0 and value.microsecond == 0

    def get_next(self):
        return TimeToken(TimeToken._next(self.value))

    def get_prev(self):
        return TimeToken(TimeToken._prev(self.value))

    @staticmethod
    def interval(start_time, end_time):
        """ Interval is end-exclusive [start_time, end_time) """
        if isinstance(start_time, time): start_time = TimeToken(start_time)
        if isinstance(end_time, time): end_time = TimeToken(end_time)
        assert isinstance(start_time, TimeToken) and isinstance(end_time, TimeToken) and end_time > start_time
        return [TimeToken(TimeToken._from_index(i)) for i in range(TimeToken._to_index(start_time.value), TimeToken._to_index(end_time))]

    @staticmethod
    def get_choices(start_time, end_time):
        return [(t.get_token(), t.display()) for t in TimeToken.interval(start_time, end_time)]

    def display(self):
        return self.value.strftime('%I:%M%p')

    def display_slice(self):
        return '%s ~ %s' % (self.display(), self.get_next().display())

    def __eq__(self, other):
        assert isinstance(other, TimeToken)
        return self.value == other.value

    def __lt__(self, other):
        assert isinstance(other, TimeToken)
        return self.value < other.value

    # this makes the class proxy
    def __getattr__(self, attrib):
        return getattr(self.value, attrib)


class TimeTokenField(models.TimeField, metaclass=models.SubfieldBase):
    description = 'A TimeField with fixed half hour point. Accept token input.'

    def to_python(self, value):
        try:
            if value is None:
                return None
            if isinstance(value, str):
                # when value is a string, it's a token.
                return TimeToken.from_token(value)
            elif isinstance(value, int):
                # when value is int, make it a string and do the same.
                return TimeToken.from_token('%04d' % value)
            elif isinstance(value, time):
                # when the value is time, go through the super one, and then return TimeToken
                _value = super(TimeTokenField, self).to_python(value)
                return TimeToken(_value)
            elif isinstance(value, TimeToken):
                # if it's just DayToken, don't change anything.
                return value
            else:
                raise ValidationError('Cannot identify TimeToken type: %s' % type(value))
        except ValueError as e:
            raise ValidationError(e)

    def get_prep_value(self, value):
        if value is None:
            return None
        assert isinstance(value, TimeToken)
        return value.value


class Slot(models.Model):
    """
    Any class that has the start_time and end_time will be subclass of this.
    """
    day = DayTokenField()

    start_time = TimeTokenField()
    end_time = TimeTokenField()

    class Meta():
        abstract = True


class OfferSlot(Slot):
    user = models.ForeignKey(User)

    @staticmethod
    def add_missing(day, user, start_time):
        assert isinstance(day, DayToken) and isinstance(user, User) and isinstance(start_time, TimeToken)
        if not OfferSlot.objects.filter(day=day, user=user, start_time=start_time, end_time=start_time.get_next()).exists():
            m = OfferSlot(day=day, user=user, start_time=start_time, end_time=start_time.get_next())
            m.save()
            return True
        else:
            return False

    @staticmethod
    def delete_existing(day, user, start_time):
        assert isinstance(day, DayToken) and isinstance(user, User) and isinstance(start_time, TimeToken)
        qs = OfferSlot.objects.filter(day=day, user=user, start_time=start_time, end_time=start_time.get_next())
        if qs.exists():
            qs.delete()
            return True
        else:
            return False

    @staticmethod
    def delete_all(day, user):
        qs = OfferSlot.objects.filter(day=day, user=user)
        if qs.exists():
            qs.delete()
            return True
        else:
            return False


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