from django.db import models
from django.contrib.auth.models import User, Group
from location.models import Center
# from phonenumber_field.modelfields import PhoneNumberField


# class UserProfile(User):
#     """
#     A proxy class for User to have profile data.
#     """
#     class Meta():
#         proxy = True
#
#     @staticmethod
#     def convert_user(user):
#         if user.__class__ == User:
#             user.__class__ = UserProfile
#
#     @staticmethod
#     def get_user_profile(user):
#         """ This will hit DB again. But will load a new clean instance"""
#         return UserProfile.objects.get(pk=user.id)
#
#     @staticmethod
#     def load(pk):
#         return UserProfile.objects.get(pk=pk)
#
#     def get_profile(self):
#         return self.profile if hasattr(self, 'profile') else None


class Profile(models.Model):
    """
    This has a one-to-one relationship with User, using user.pk as pk.
    A "profile" instance is bound to have a "user" object, but not vice versa.
    Business logic about users should all happen here.
    """
    user = models.OneToOneField(User, primary_key=True)
    address = models.CharField(max_length=200, blank=True)
    # giver = models.BooleanField(default=False)
    # taker = models.BooleanField(default=False)
    # phone_main = PhoneNumberField(max_length=20)
    # phone_backup = PhoneNumberField(max_length=20, blank=True)
    phone_main = models.CharField(max_length=12)
    phone_backup = models.CharField(max_length=12, blank=True)

    # for center related stuff.
    centers = models.ManyToManyField(Center, limit_choices_to={'status': True})
    verified = models.NullBooleanField()

    def __str__(self):
        return self.user.get_full_name()

    # @staticmethod
    # def get_profile(user):
    #     return Profile.objects.get(pk=user.id)


# class FullUser(User):
#     """
#     This class extends User but does not replace AUTH_MODULE. It will have the same PK as User object, which is
#     different from using the "profile" design pattern where Profile has its own PK.
#     """
#     address = models.CharField(max_length=200, blank=True)
#     phone_main = models.CharField(max_length=12, blank=True)
#     phone_backup = models.CharField(max_length=12, blank=True)
#
#     # for center related fields if the user belongs to "center" related groups
#     centers = models.ManyToManyField(Center)
#     validated = models.NullBooleanField()
#
#     class Meta(User.Meta):
#         verbose_name = 'full user'
#         verbose_name_plural = 'full users'


# class Role(Group):
#     # human readable name
#     title = models.CharField(max_length=50)
#     # giver = models.BooleanField(default=False)
#     # taker = models.BooleanField(default=False)
#     function_center = models.BooleanField(default=False)


class Role(models.Model):
    """
    This has one-one relationship to auth.Group instead of inherit from Group.
    """
    group = models.OneToOneField(Group, primary_key=True)
    machine_name = models.SlugField(max_length=50)
    # specify whether this role is to function for children centers.
    type_center = models.BooleanField(default=False)


# class Staff(Profile):
#     """
#     Staff are those who work for a center.
#     Directors are also staff, but are defined in django "group" in order to have more permissions.
#     """
#     ROLE_DIRECTOR = 1
#     ROLE_TEACHER = 2    # full-time
#     ROLE_SUPPORT = 3    # part-time
#     ROLE_INTERN = 4     # student
#     ROLES = (
#         (ROLE_DIRECTOR, 'Director'),
#         (ROLE_TEACHER, 'Teacher'),
#         (ROLE_SUPPORT, 'NC Support'),
#         (ROLE_INTERN, 'Student Intern'),
#     )
#     role = models.PositiveSmallIntegerField(choices=ROLES)
#
#     centers = models.ManyToManyField(Center)
#     checked = models.BooleanField(default=False)