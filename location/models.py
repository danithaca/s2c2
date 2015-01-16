from collections import OrderedDict
from datetime import time

from django.db import models
from django.contrib.auth.models import User
from localflavor.us.models import USStateField
from pytz import timezone


class Area(models.Model):
    name = models.CharField(max_length=50)
    state = USStateField()

    def get_timezone(self):
        if self.state == 'MI':
            return timezone('US/Eastern')

    def __str__(self):
        return '%s - %s' % (self.name, self.state)


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


class Classroom(Location):
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

    def get_unmet_table(self, day):
        """ return the table data to display staff availability based on classroom needs. """
        from user.models import UserProfile
        from slot.models import OfferSlot, NeedSlot, TimeToken
        table = []
        for t in NeedSlot.objects.filter(location=self, day=day, meet__isnull=True).values_list('start_time', flat=True).distinct().order_by('start_time'):
            start_time = TimeToken(t)
            first_col = start_time
            second_col = [UserProfile.get_by_id(pk=pk) for pk in OfferSlot.get_unmet_slot_owner_id(day, start_time)]
            table.append((first_col, second_col))
        return table