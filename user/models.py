from datetime import time

from django.db import models
from django.contrib.auth.models import User, Group

from location.models import Center


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
        """ Factory method. Load UserProfile or its subclass based on which role the user is in. """
        p = UserProfile(User.objects.get(pk=pk))
        if p.is_center_staff():
            return CenterStaff(p.user)
        else:
            return p

    @staticmethod
    def get_by_id_default(pk, default_user):
        try:
            u = User.objects.get(pk=pk)
        except User.DoesNotExist as e:
            u = default_user
        return UserProfile.get_by_id(u.pk)

    def has_profile(self):
        return self.profile is not None

    def is_verified(self):
        return self.has_profile() and self.profile.verified is True

    def get_groups_id_set(self):
        return set(self.user.groups.values_list('pk', flat=True))

    def is_center_manager(self):
        if not GroupRole.get_center_manager_role_id_set().isdisjoint(self.get_groups_id_set()):
            return True
        else:
            return False

    def is_center_staff(self):
        if not GroupRole.get_center_staff_role_id_set().isdisjoint(self.get_groups_id_set()):
            return True
        else:
            return False

    def get_display_name(self, short=False):
        name = self.user.get_full_name() if not short else self.user.get_short_name()
        if len(name) == 0:
            name = self.user.get_username()
        return name

    def __getattr__(self, attrib):
        if self.has_profile() and hasattr(self.profile, attrib):
            return getattr(self.profile, attrib)
        return getattr(self.user, attrib)


class CenterStaff(UserProfile):
    """ Provide additional functions if the user is a center staff. """
    def __init__(self, user):
        super(CenterStaff, self).__init__(user)
        assert self.is_center_staff()

    def get_slot_table(self, day):
        """ This is to prepare data for the table in "staff" view. """
        from slot.models import TimeToken, OfferSlot
        data = []
        for start_time in TimeToken.interval(time(7), time(19, 30)):
            end_time = start_time.get_next()
            # start_time and end_time has to be wrapped inside of TimeToken in filter.
            # TimeTokenField.to_python() is not called because objects.filter() doesn't create a new TimeTokenField() instance.
            data.append(((start_time, end_time),
                        OfferSlot.objects.filter(day=day, user=self.user, start_time=start_time, end_time=end_time)))
        return data


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
        # someday: make it cache or load in "class".
        # however, when put as class property, django will complain with error. perhaps because Role.objects are not loaded yet.
        center_staff_role_id_set = set(Role.objects.filter(machine_name__in=('teacher', 'support', 'intern')).values_list('pk', flat=True))
        return center_staff_role_id_set

    @staticmethod
    def get_center_manager_role_id_set():
        center_manager_role_id_set = set(Role.objects.filter(machine_name='manager').values_list('pk', flat=True))
        return center_manager_role_id_set

