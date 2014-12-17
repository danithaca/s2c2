from django.db import models
from django.contrib.auth.models import User
from location.models import Center
from phonenumber_field.modelfields import PhoneNumberField


class Profile(models.Model):
    user = models.OneToOneField(User)
    address = models.CharField(max_length=200, blank=True)
    # giver = models.BooleanField(default=False)
    # taker = models.BooleanField(default=False)
    phone_main = PhoneNumberField(max_length=20)
    phone_backup = PhoneNumberField(max_length=20, blank=True)

    def __str__(self):
        return self.user.get_full_name()


class Staff(Profile):
    """
    Staff are those who work for a center.
    Directors are also staff, but are defined in django "group" in order to have more permissions.
    """
    ROLE_DIRECTOR = 1
    ROLE_TEACHER = 2    # full-time
    ROLE_SUPPORT = 3    # part-time
    ROLE_INTERN = 4     # student
    ROLES = (
        (ROLE_DIRECTOR, 'Director'),
        (ROLE_TEACHER, 'Teacher'),
        (ROLE_SUPPORT, 'NC Support'),
        (ROLE_INTERN, 'Student Intern'),
    )
    role = models.PositiveSmallIntegerField(choices=ROLES)
    centers = models.ManyToManyField(Center)
    checked = models.BooleanField(default=False)