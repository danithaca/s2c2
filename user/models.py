from collections import defaultdict
from datetime import time
import warnings
from django.core.urlresolvers import reverse

from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from image_cropping import ImageCropField, ImageRatioField
from localflavor.us.models import PhoneNumberField
from location.models import Center, Area, Classroom
from slot.models import TemplateSettings


class Profile(TemplateSettings):
    """
    This has a one-to-one relationship with User, using user.pk as pk.
    A "profile" instance is bound to have a "user" object, but not vice versa.
    Business logic about users should all happen here.
    """
    user = models.OneToOneField(User, primary_key=True)
    address = models.CharField(max_length=200, blank=True)
    # phone_main = models.CharField(max_length=12)
    # phone_backup = models.CharField(max_length=12, blank=True)
    phone_main = PhoneNumberField(blank=True)
    phone_backup = PhoneNumberField(blank=True)

    # for center related stuff.
    # fixme: should limit to centers in the same area as the user.
    centers = models.ManyToManyField(Center, limit_choices_to={'status': True}, blank=True)
    verified = models.NullBooleanField()
    note = models.TextField(blank=True, null=True)
    # picture = models.ImageField(upload_to='picture', blank=True, null=True)
    picture_original = ImageCropField(upload_to='picture', blank=True, null=True)
    picture_cropping = ImageRatioField('picture_original', '200x200')

    # currently we use the default Area for all new users. but we should remove default later.
    area = models.ForeignKey(Area, default=1)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

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

    def get_centers_id_set(self):
        if self.has_profile():
            return set(self.profile.centers.values_list('pk', flat=True))
        else:
            return set([])

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
        warnings.warn('Deprecated in favor of filter "nice_name"', DeprecationWarning)
        name = self.user.get_full_name() if not short else self.user.get_short_name()
        if len(name) == 0:
            name = self.user.get_username()
        return name

    def __getattr__(self, attrib):
        if self.has_profile() and hasattr(self.profile, attrib):
            return getattr(self.profile, attrib)
        return getattr(self.user, attrib)

    def __eq__(self, other):
        if isinstance(other, UserProfile):
            return self.user == other.user
        else:
            return self.user.__eq__(other)

    def is_same_center(self, target):
        """
        :param target: The target, could be another user or a classroom or a center
        :return: True if they belong to the same center, or false.
        """
        if isinstance(target, UserProfile):
            return not self.get_centers_id_set().isdisjoint(target.get_centers_id_set())
        elif isinstance(target, User):
            return self.is_same_center(UserProfile(target))
        elif isinstance(target, Center):
            return target.id in self.get_centers_id_set()
        elif isinstance(target, Classroom):
            return target.center.id in self.get_centers_id_set()
        else:
            assert False

    def display_role(self):
        return ', '.join(self.user.groups.values_list('name', flat=True))

    def get_center_role(self):
        # use this instead of "user.groups" because we want to do ordering and filtering.
        # ordering is automatically by 'id' using last(). the last 'id' is the most recent role assignment.
        g = Group.objects.filter(user=self.user, role__type_center=True).last()
        return GroupRole(g) if g is not None else None

    def has_picture(self):
        return self.has_profile() and self.profile.picture_original and self.profile.picture_cropping

    def get_active_classrooms(self):
        """ return the list of classroom associated with the user. ordered by most recent activity. """
        #assert self.is_center_manager() or self.is_center_staff()

        if self.is_center_manager():
            return [c for c in Classroom.objects.filter(status=True, center__in=self.profile.centers.all()).order_by('center', 'name').distinct()]
        elif self.is_center_staff():
            # might need to order by recency.
            # order_by() doesn't work very well with distinct()
            return [c for c in Classroom.objects.filter(status=True, needslot__meet__offer__user=self.user).order_by('center', 'name').distinct()]
        else:
            return []

    def picture_link(self):
        from s2c2.templatetags.s2c2_tags import user_picture_url
        return user_picture_url(None, self)


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

    # this is to get data for the dashboard
    def get_week_table(self, day):
        from slot.models import DayToken, TimeToken, OfferSlot
        weekday = day.expand_week()[:5]    # only take workdays
        time_per_day = TimeToken.interval(time(7, 30), time(19))

        data = defaultdict(lambda: defaultdict(list))
        for offer in OfferSlot.objects.filter(day__in=weekday, user=self.user):
            data[offer.day][offer.start_time].append(offer)

        rows = []
        for t in time_per_day:
            row = []
            for d in weekday:
                row.append(data[d][t])  # append either [] of [offer...] to row.
            rows.append([t, row])

        return {'header': weekday,  'rows_header': time_per_day, 'rows': rows}

    def get_unmet_offer_by_day(self, day):
        """ Return a list of offers from the user on the day. """
        from slot.models import OfferSlot
        return OfferSlot.objects.filter(user=self.user, day=day, meet__isnull=True).order_by('start_time')

    def get_unmet_table(self, day):
        """ return the table data to display classroom needs based on the user's availability. """
        from location.models import Classroom
        from slot.models import NeedSlot
        table = []
        for unmet_offer in self.get_unmet_offer_by_day(day):
            first_col = unmet_offer.start_time
            second_col = [Classroom.objects.get(pk=pk) for pk in NeedSlot.get_unmet_slot_owner_id(day, unmet_offer.start_time)]
            table.append((first_col, second_col))
        return table

    def get_week_hours(self, day):
        from slot.models import TimeToken, OfferSlot
        count = [0, 0, 0]
        weekday = day.expand_week()
        for offer in OfferSlot.objects.filter(day__in=weekday, user=self.user):
            count[0] += 1
            try:
                m = offer.meet
                count[1] += 1
            except ObjectDoesNotExist:
                count[2] += 1
        return tuple([str(TimeToken.convert_slot_count_to_hours(i)) for i in count])


class Role(models.Model):
    """
    This has one-one relationship to auth.Group instead of inherit from Group.
    """
    group = models.OneToOneField(Group, primary_key=True)
    machine_name = models.SlugField(max_length=50)
    # specify whether this role is to function for children centers.
    type_center = models.BooleanField(default=False)


class GroupRole(object):
    all_valid_roles = ('manager', 'teacher', 'support', 'intern')
    center_staff_roles = ('teacher', 'support', 'intern')
    center_manager_roles = ('manager', )

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

    @staticmethod
    def get_center_roles_choices():
        return [(0, '- Select -')] + [(g.pk, g.name) for g in Group.objects.filter(role__type_center=True).order_by('id')]

