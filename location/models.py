from datetime import time

from django.db import models
from django.contrib.auth.models import User


class Location(models.Model):
    # owner = models.ForeignKey(auth.get_user_model())
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=200, blank=True)
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
    # no more data to add
    pass


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