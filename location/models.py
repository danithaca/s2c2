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

    def get_slot_table_regular(self, dow):
        """ This is to prepare data for the table in "classroom_regular" view. """
        # to avoid cylic module import
        from slot.models import HalfHourTime, NeedRegular
        data = []
        for t in HalfHourTime.interval(time(hour=7), time(hour=19, minute=30)):
            t_obj = HalfHourTime(t)
            data.append((str(t_obj),
                         NeedRegular.objects.filter(start_dow=dow, location=self, start_time=t_obj.start_time, end_time=t_obj.end_time)))
        return data
