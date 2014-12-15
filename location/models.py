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


class Center(Location):
    # no more data to add
    pass


class Classroom(Location):
    center = models.ForeignKey(Center)