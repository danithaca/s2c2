from abc import ABCMeta, abstractstaticmethod, abstractmethod
from functools import total_ordering
import calendar
from itertools import groupby
import re
from datetime import time, timedelta, datetime, date

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

from location.models import Location


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

    @staticmethod
    def today():
        return DayToken(datetime.today().date())

    def __eq__(self, other):
        # we don't do assertion here because django sometimes compare this to '' (empty string)
        # assert isinstance(other, DayToken), 'Invalid: comparing DayToken to type %s with value "%s".' % (type(other), str(other))
        if isinstance(other, DayToken):
            return self.value == other.value
        else:
            return False

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

    def switch(self):
        if self.is_regular():
            return self.date_of_weekday()
        else:
            return self.weekday_of_date()

    def expand_week(self):
        if self.is_regular():
            return [DayToken(d) for d in DayToken.weekday_tuple]
        else:
            return [DayToken(self.value - timedelta(days=i)) for i in range(self.weekday(), 0, -1)] + [self, ]\
                   + [DayToken(self.value + timedelta(days=i+1)) for i in range(6 - self.weekday())]

    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return self.value.__hash__()

    def date_of_weekday(self):
        assert self.is_regular()
        this_week = DayToken.today().expand_week()
        return this_week[self.weekday()]

    def weekday_of_date(self):
        assert not self.is_regular()
        return DayToken(DayToken.weekday_tuple[self.weekday()])

    @staticmethod
    def get_weekday_list(working_day_only=False):
        result = [DayToken(d) for d in DayToken.weekday_tuple]
        if working_day_only:
            return result[0:5]
        else:
            return result


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

    @staticmethod
    def convert_slot_count_to_hours(count):
        return count / 2

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
        return [TimeToken(TimeToken._from_index(i)) for i in range(TimeToken._to_index(start_time.value), TimeToken._to_index(end_time.value))]

    @staticmethod
    def get_choices(start_time, end_time):
        return [(t.get_token(), t.display()) for t in TimeToken.interval(start_time, end_time)]

    def display(self):
        return self.value.strftime('%I:%M%p')

    def display_slice(self):
        return '%s ~ %s' % (self.display(), self.get_next().display())

    def __eq__(self, other):
        # we don't do assertion here because django sometimes compare this to '' (empty string)
        # assert isinstance(other, TimeToken)
        if isinstance(other, TimeToken):
            return self.value == other.value
        else:
            return False

    def __lt__(self, other):
        assert isinstance(other, TimeToken)
        return self.value < other.value

    def __str__(self):
        return self.value.__str__()

    def __hash__(self):
        return self.value.__hash__()

    # this makes the class proxy
    # def __getattr__(self, attrib):
    #     return getattr(self.value, attrib)


class TimeTokenField(models.TimeField, metaclass=models.SubfieldBase):
    description = 'A TimeField with fixed half hour point. Accept token input.'

    def to_python(self, value):
        try:
            if value is None:
                return None
            if isinstance(value, str):
                # when value is a string, it's a token.
                return TimeToken.from_token(value)
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


class TimeSlot(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def display(self):
        ftime = '%I:%M%p'
        return '%s ~ %s' % (self.start.strftime(ftime), self.end.strftime(ftime))

    @staticmethod
    def combine(list_timetoken):
        assert len(list_timetoken) > 0
        combined = []
        list_index = [TimeToken._to_index(t.value) for t in list_timetoken]
        sorted(list_index)
        for k, g in groupby(enumerate(list_index), lambda x: x[1] - x[0]):
            l = list(g)
            combined.append(TimeSlot(TimeToken._from_index(l[0][1]), TimeToken._from_index((l[-1][1] + 1) % 48)))
        return combined

    @staticmethod
    def display_combined(list_timetoken):
        return ', '.join([t.display() for t in TimeSlot.combine(list_timetoken)])


class Slot(models.Model):
    """
    Any class that has the start_time and end_time will be subclass of this.
    """
    day = DayTokenField()

    start_time = TimeTokenField()
    end_time = TimeTokenField()

    class Meta():
        abstract = True

    @staticmethod
    @abstractmethod
    def get_unmet_slot_owner_id(day, star): pass


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

    @staticmethod
    def get_available_offer(day, start_time):
        return [o for o in OfferSlot.objects.filter(day=day, start_time=start_time, end_time=start_time.get_next(), meet__isnull=True, user__profile__verified=True)]

    @staticmethod
    def get_unmet_slot_owner_id(day, start_time):
        # fixme: need to filter by center
        return OfferSlot.objects.filter(day=day, start_time=start_time, end_time=start_time.get_next(), meet__isnull=True).values_list('user_id', flat=True).distinct()

    def __str__(self):
        return '%s: %s %s ~ %s' % (self.user.username, self.day.get_token(), self.start_time.display(), self.end_time.display())

    @staticmethod
    def copy(user, target_day):
        """ copy template from day.weekday to the day for the user. """
        assert not target_day.is_regular()
        template_day = target_day.weekday_of_date()

        template_data = {s.start_time: s for s in OfferSlot.objects.filter(user=user, day=template_day)}
        target_data = {s.start_time: s for s in OfferSlot.objects.filter(user=user, day=target_day)}

        # add
        for t in set(template_data.keys()).difference(set(target_data.keys())):
            OfferSlot.objects.create(user=user, day=target_day, start_time=t, end_time=t.get_next())

        # delete
        for t in set(target_data.keys()).difference(set(template_data.keys())):
            target_data[t].delete()


class NeedSlot(Slot):
    location = models.ForeignKey(Location)

    def __str__(self):
        return '%s: %s %s ~ %s' % (self.location.name, self.day.get_token(), self.start_time.display(), self.end_time.display())

    @staticmethod
    def delete_empty(location, day, start_time):
        qs = NeedSlot.objects.filter(location=location, day=day, start_time=start_time, end_time=start_time.get_next()).exclude(meet__isnull=False)
        if qs.exists():
            qs.delete()
            return True
        else:
            return False

    @staticmethod
    def delete_cascade(location, day, start_time):
        qs = NeedSlot.objects.filter(location=location, day=day, start_time=start_time, end_time=start_time.get_next())
        if qs.exists():
            qs.delete()
            return True
        else:
            return False

    @staticmethod
    def get_unmet_slot_owner_id(day, start_time):
        # fixme: need to filter by center
        return NeedSlot.objects.filter(day=day, start_time=start_time, end_time=start_time.get_next(), meet__isnull=True).values_list('location_id', flat=True).distinct()

    @staticmethod
    def copy(location, target_day):
        """ copy template from day.weekday to the day for the location. """
        assert not target_day.is_regular()
        template_day = target_day.weekday_of_date()

        # someday: this is not optimal by deleting everything first and add.
        # should keep existing matches and add/delete only when necessary.
        NeedSlot.objects.filter(location=location, day=target_day).delete()
        to_save = [NeedSlot(location=location, day=target_day, start_time=s.start_time, end_time=s.end_time)
                   for s in NeedSlot.objects.filter(location=location, day=template_day)]
        NeedSlot.objects.bulk_create(to_save)

    @staticmethod
    def get_or_create_unmet_need(location, day, start_time, end_time):
        qs = NeedSlot.objects.filter(location=location, day=day, start_time=start_time, end_time=end_time, meet__isnull=True)
        if not qs.exists():
            n = NeedSlot(location=location, day=day, start_time=start_time, end_time=end_time)
            n.save()
            return n
        else:
            return qs.first()


# class MeetSlot(Slot):
#     offer = models.ForeignKey(OfferSlot)
#     need = models.ForeignKey(NeedSlot)
#
#     # only 1 meet could be "active" that associate the same "offer" and "need".
#     # there's no db reinforcement, need to check in the code.
#
#     INACTIVE = 0
#     MAIN = 1
#     BACKUP = 20
#     MEET_STATUS = (
#         (INACTIVE, 'inactive'),
#         (MAIN, 'main'),
#         (BACKUP, 'backup'),
#     )
#     status = models.PositiveSmallIntegerField(choices=MEET_STATUS, default=INACTIVE)


# we are making Meet to be one-one relationship to offer/need, and not extends from Slot.
# if there's going to be more complex workflow state, might create a new model instead of using Meet.
class Meet(models.Model):
    offer = models.OneToOneField(OfferSlot, primary_key=True)
    need = models.OneToOneField(NeedSlot, primary_key=True)

    def __str__(self):
        assert self.need.day == self.offer.day and self.need.start_time == self.offer.start_time and self.need.end_time == self.offer.end_time
        return '%s (%s): %s - %s' % (self.need.day.get_token(), self.need.start_time.display_slice(), self.need.location.name, self.offer.user.username)

    @staticmethod
    def copy_by_location(location, target_day):
        """ copy template from day.weekday to the day for the location. """
        assert not target_day.is_regular()
        template_day = target_day.weekday_of_date()

        # this doesn't work which throws: "Can only delete one table at a time."
        # Meet.objects.filter(need__location=location, need__day=target_day).delete()

        # someday: this is not optimal by deleting everything first and add.
        to_delete = Meet.objects.filter(need__location=location, need__day=target_day)
        for m in to_delete:
            m.delete()

        for m in Meet.objects.filter(need__location=location, need__day=template_day):
            offer, created = OfferSlot.objects.get_or_create(user=m.offer.user, day=target_day, start_time=m.offer.start_time, end_time=m.offer.end_time, meet__isnull=True)
            need = NeedSlot.get_or_create_unmet_need(location=m.need.location, day=target_day, start_time=m.need.start_time, end_time=m.need.end_time)
            Meet.objects.create(offer=offer, need=need)
