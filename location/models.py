from collections import OrderedDict, defaultdict
from datetime import time
from itertools import cycle

from django.db import models
from django.contrib.auth.models import User
from localflavor.us.models import USStateField
from pytz import timezone
from s2c2 import settings
from s2c2.models import TemplateSettings
from django.conf import settings


class Area(models.Model):
    name = models.CharField(max_length=50)
    state = USStateField()
    description = models.TextField(blank=True)

    def get_timezone(self):
        if self.state == 'MI':
            return timezone('US/Eastern')

    def __str__(self):
        return '%s - %s' % (self.name, self.state)

    @staticmethod
    def default():
        return Area.objects.get(pk=1)


class Location(models.Model):
    """ A location is a place to create "Need" object. """

    # owner = models.ForeignKey(auth.get_user_model())
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_by_id(pk):
        """ Factory method. Load Location or its subclass based on type. """
        try:
            c = Center.objects.get(pk=pk)
            return c
        except Center.DoesNotExist as e:
            pass

        try:
            c = Classroom.objects.get(pk=pk)
            return c
        except Classroom.DoesNotExist as e:
            pass

        return Location.objects.get(pk=pk)

    @staticmethod
    def init_special_list():
        Location.MEETING = Location.objects.get(name='- Meeting -', address='Administration', status=True)
        Location.VACATION = Location.objects.get(name='- Vacation -', address='Administration', status=True, owner_id=1)
        Location.UNAVAILABLE = Location.objects.get(name='- Unavailable -', address='Administration', status=True, owner_id=1)
        Location.SPECIAL_LIST = [Location.MEETING, Location.VACATION, Location.UNAVAILABLE]

    @staticmethod
    def get_special_list():
        try:
            return Location.SPECIAL_LIST
        except AttributeError as e:
            Location.init_special_list()
            return Location.SPECIAL_LIST

    @staticmethod
    def get_special_list_id_set():
        return set([l.id for l in Location.get_special_list()])


class Center(Location):
    area = models.ForeignKey(Area)

    # def get_associates_data(self):
    #     from user.models import GroupRole
    #     manager_group = GroupRole.get_by_name('manager')
    #     teacher_group = GroupRole.get_by_name('teacher')
    #     support_group = GroupRole.get_by_name('support')
    #     intern_group = GroupRole.get_by_name('intern')
    #
    #     return OrderedDict((
    #         ('Classroom', Classroom.objects.filter(center=self)),
    #         (manager_group.name, User.objects.filter(profile__centers=self, groups=manager_group.group, is_active=True)),
    #         (teacher_group.name, User.objects.filter(profile__centers=self, groups=teacher_group.group, is_active=True)),
    #         (support_group.name, User.objects.filter(profile__centers=self, groups=support_group.group, is_active=True)),
    #         (intern_group.name, User.objects.filter(profile__centers=self, groups=intern_group.group, is_active=True)),
    #     ))

    def get_managers(self):
        return User.objects.filter(profile__centers=self, groups__role__machine_name='manager', is_active=True)

    def get_classroom_color(self):
        list_classroom = Classroom.objects.filter(center=self, status=True).order_by('name')
        return zip(list_classroom, cycle(settings.COLORS))


class Classroom(Location, TemplateSettings):
    center = models.ForeignKey(Center)

    def get_slot_table(self, day):
        """ This is to prepare data for the table in "classroom" view. """
        # to avoid cyclic module import
        from slot.models import TimeToken, NeedSlot
        data = []
        for start_time in TimeToken.interval(time(7), time(19, 30)):
            end_time = start_time.get_next()
            # start_time and end_time has to be wrapped inside of TimeToken in filter.
            # TimeTokenField.to_python() is not called because objects.filter() doesn't create a new TimeTokenField() instance.
            data.append(((start_time, end_time),
                         NeedSlot.objects.filter(day=day, location=self, start_time=start_time, end_time=end_time)))
        return data

    # this is to get data for the dashboard
    def get_week_table(self, day):
        from slot.models import TimeToken, NeedSlot
        weekday = day.expand_week()[:5]    # only take workdays
        time_per_day = TimeToken.interval(time(7, 30), time(19))

        data = defaultdict(lambda: defaultdict(list))
        for need in NeedSlot.objects.filter(day__in=weekday, location=self):
            data[need.day][need.start_time].append(need)

        rows = []
        for t in time_per_day:
            row = []
            for d in weekday:
                row.append(data[d][t])  # append either [] of [need...] to row.
            rows.append([t, row])

        return {'header': weekday,  'rows_header': time_per_day, 'rows': rows}

    def get_unmet_table(self, day):
        """ return the table data to display staff availability based on classroom needs. """
        from user.models import UserProfile
        from slot.models import OfferSlot, NeedSlot, TimeToken
        table = []
        for t in NeedSlot.objects.filter(location=self, day=day, meet__isnull=True).values_list('start_time', flat=True).distinct().order_by('start_time'):
            start_time = TimeToken(t)
            first_col = start_time
            user_id_list = OfferSlot.objects.filter(day=day, start_time=start_time, end_time=start_time.get_next(), meet__isnull=True, user__profile__verified=True, user__profile__centers=self.center).values_list('user_id', flat=True).distinct()
            second_col = [UserProfile.get_by_id(pk=pk) for pk in user_id_list]
            table.append((first_col, second_col))
        return table

    def get_unmet_need_time(self, day):
        from slot.models import NeedSlot, TimeToken
        l = [TimeToken(t) for t in NeedSlot.objects.filter(location=self, day=day, meet__isnull=True).values_list('start_time', flat=True).distinct().order_by('start_time')]
        return l

    def get_staff(self, day=None):
        from slot.models import Meet
        if day is None:
            qs = User.objects.filter(offerslot__meet__need__location=self).annotate(num_slot=models.Count('offerslot')).order_by('-num_slot')
        else:
            qs = User.objects.filter(offerslot__meet__need__location=self, offerslot__day=day).annotate(num_slot=models.Count('offerslot')).order_by('-num_slot')
        return [s for s in qs]

    def exists_unmet_need(self, day):
        from slot.models import NeedSlot
        weekday = day.expand_week()
        return NeedSlot.objects.filter(day__in=weekday, location=self, meet__isnull=True).exists()

    def copy_week_schedule(self, from_day, to_day):
        from slot.models import NeedSlot, Meet
        assert from_day != to_day
        from_week = from_day.expand_week()
        to_week = to_day.expand_week()
        assert from_week != to_week
        assert len(from_week) == len(to_week)

        failed = []
        for from_day, to_day in zip(from_week, to_week):
            assert from_day.weekday() == to_day.weekday()
            try:
                NeedSlot.safe_copy(self, from_day, to_day)
                Meet.safe_copy_by_location(self, from_day, to_day)
            except ValueError as e:
                failed.append(to_day)

        return failed
