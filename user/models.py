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
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()

    # @staticmethod
    # def get_profile(user):
    #     return Profile.objects.get(pk=user.id)


class UserProfile(object):
    """
    A proxy to django-user. Note the __getattr__() override.
    """
    def __init__(self, user):
        assert user is not None and isinstance(user, User)
        self.user = user
        try:
            self.profile = self.user.profile
        except Profile.DoesNotExist as e:
            self.profile = None

    @staticmethod
    def get_by_id(pk):
        return UserProfile(User.objects.get(pk=pk))

    def has_profile(self):
        return self.profile is not None

    def is_verified(self):
        return self.has_profile() and self.profile.verified is True

    def get_groups_id_set(self):
        return set(self.user.groups.values_list('pk', flat=True))

    def is_center_manager(self):
        manager_role = GroupRole.get_by_name('manager')
        if self.is_verified() and manager_role is not None and manager_role.pk in self.get_groups_id_set():
            return True
        else:
            return False

    def is_center_staff(self):
        if self.is_verified() and not GroupRole.get_center_staff_role_id_set().isdisjoint(self.get_groups_id_set()):
            return True
        else:
            return False

    def __getattr__(self, attrib):
        if self.has_profile() and hasattr(self.profile, attrib):
            return getattr(self.profile, attrib)
        return getattr(self.user, attrib)


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


class GroupRole(object):
    def __init__(self, group):
        assert group is not None and isinstance(group, Group)
        self.group = group
        # we assume all group has a role, or we'll raise exception.
        self.role = group.role

    def __getattr__(self, attrib):
        if hasattr(self.role, attrib):
            return getattr(self.role, attrib)
        return getattr(self.group, attrib)

    @property
    def pk(self):
        assert self.group.pk == self.role.pk
        return self.group.pk

    @staticmethod
    def get_by_name(name):
        role = Role.objects.get(machine_name=name)
        return GroupRole(role.group)

    @staticmethod
    def get_center_staff_role_id_set():
        # TODO: might want to cache it.
        # return set([GroupRole.get_by_name(n).pk for n in center_staff_role])
        return set(Role.objects.filter(machine_name__in=('teacher', 'support', 'intern')).values_list('pk', flat=True))


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