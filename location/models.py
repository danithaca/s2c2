from django.db import models
from django.contrib.auth.models import User
from localflavor.us.models import USStateField
from pytz import timezone


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


class Center(Location):
    area = models.ForeignKey(Area)


class TemplateSettings(models.Model):
    template_base_date = models.DateField(blank=True, null=True, help_text='Pick a date of which the weekly schedule would be the template for automatic copy.')
    template_copy_ahead = models.CharField(default='none', max_length=10, choices=(
        ('none', 'None'),
        ('1week', '1 week ahead'),
        ('2week', '2 weeks ahead'),
        ('3week', '3 weeks ahead'),
        ('4week', '4 weeks ahead'),
    ), help_text='How much ahead to copy the template.')

    class Meta:
        abstract = True


class Classroom(Location, TemplateSettings):
    center = models.ForeignKey(Center)
