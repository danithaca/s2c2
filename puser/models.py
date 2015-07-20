from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from image_cropping import ImageCropField, ImageRatioField
from localflavor.us.models import PhoneNumberField
from django.core import checks
from circle.models import Membership, Circle
from p2 import settings
from s2c2.utils import auto_user_name, deprecated


@checks.register()
def email_duplicate_check(app_configs, **kwargs):
    errors = []
    if app_configs is None or 'puser' in [a.label for a in app_configs]:
        from django.contrib.auth.models import User
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute('SELECT email, COUNT(*) FROM ' + User._meta.db_table + ' GROUP BY email HAVING COUNT(*) > 1')
        rows = cursor.fetchall()
        if len(rows) > 0:
            errors.append(checks.Warning('Duplicate user email exits: %s' % len(rows)))
    return errors


class Info(models.Model):
    """
    The extended field for p2 Users.
    Authentication/authorization would be handled by user_account.
    """

    user = models.OneToOneField(User, primary_key=True)
    address = models.CharField(max_length=200, blank=True)
    phone = PhoneNumberField(blank=True)
    note = models.TextField(blank=True)

    picture_original = ImageCropField(upload_to='picture', blank=True, null=True)
    picture_cropping = ImageRatioField('picture_original', '200x200')

    from location.models import Area
    # user's home area. it doesn't necessarily mean the user will request/respond to this area only.
    area = models.ForeignKey(Area, default=1)

    # note: use User.is_active instead.
    # False:     the user has setup a password, and is able to login (not necessarily filled out anything)
    # True:    just created a user stub with email only.
    # stub = models.BooleanField()

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @staticmethod
    def get_or_create_for_user(user):
        assert isinstance(user, User)
        from location.models import Area
        info, created = Info.objects.get_or_create(user=user, defaults={
            'area': Area.objects.get(pk=1)
        })
        return info


class PUser(User):
    """
    This is the proxy class for User instead of using monkey patch.
    """

    class Meta:
        proxy = True

    # def __getattr__(self, attrib):
    #     if self.has_info() and hasattr(self.info, attrib):
    #         return getattr(self.info, attrib)
    #     elif hasattr(self, attrib):
    #         return getattr(self, attrib)
    #     else:
    #         raise AttributeError

    def get_absolute_url(self):
        return reverse('account_view', kwargs={'pk': self.id})

    @staticmethod
    def from_user(user):
        return PUser.objects.get(pk=user.id)

    def get_area(self):
        try:
            return self.info.area
        except Info.DoesNotExist:
            return None

    # def join(self, circle):
    #     """
    #     This is very simple, doesn't handle "approval" notification, etc.
    #     """
    #     membership, created = Membership.objects.update_or_create(member=self, circle=circle, defaults={'active': True})
    #     return membership

    # a person could have multiple personal list based on area.
    def get_personal_circle(self, area=None):
        if area is None:
            area = self.get_area()
        circle, created = Circle.objects.get_or_create(type=Circle.Type.PERSONAL.value, owner=self, area=area, defaults={
            'name': 'personal'
        })
        return circle

    @staticmethod
    def create_dummy(email):
        """
        Create a new "stub" user
        :return: the created puser object
        """
        # todo: check duplicate email
        user = PUser()
        user.username = auto_user_name(email)
        user.email = email
        user.set_unusable_password()
        user.is_active = False
        user.save()
        return user

    # this function is convenient but we still don't want to have it because "create" involves many instances
    # (Info, Account, EmailAddress) which are very situational.
    # @staticmethod
    # def get_or_create(email):
    #     try:
    #         puser = PUser.objects.get(email=email)
    #         return puser
    #     except PUser.DoesNotExist:
    #         return PUser.create_dummy(email)

    @staticmethod
    def get_by_email(email):
        return PUser.objects.get(email=email)

    def has_info(self):
        try:
            self.info
            return True
        except Info.DoesNotExist:
            return False

    def get_info(self):
        return Info.get_or_create_for_user(self)

    def has_picture(self):
        return self.has_info() and self.info.picture_original and self.info.picture_cropping

    def picture_link(self):
        from p2.templatetags.p2_tags import user_picture_url
        return user_picture_url(None, self)

    # todo: add caching mechanism here. manually deal with cache key-value pairs.
    def trusted(self, puser):
        """
        Return whether the "self" user trust the puser in parameter. The relationship doesn't have to be mutual.
        """
        if isinstance(puser, User):
            puser = PUser.from_user(puser)
        assert isinstance(puser, PUser)

        # always trust one's self.
        if self == puser:
            return True

        # trust someone in my personal circle
        my_personal_circles = Circle.objects.filter(type=Circle.Type.PERSONAL.value, owner=self)
        if Membership.objects.filter(circle__in=my_personal_circles, member=puser, active=True).exists():
            return True

        # trust someone i'm part of her personal circle which I approved
        their_personal_circles = Circle.objects.filter(type=Circle.Type.PERSONAL.value, owner=puser)
        if Membership.objects.filter(circle__in=their_personal_circles, member=self, approved=True).exists():
            return True

        # trust someone in the public circles where I'm a member of.
        my_public_circles = Circle.objects.filter(type=Circle.Type.PUBLIC.value, membership__member=self, membership__active=True, membership__approved=True)
        if Membership.objects.filter(circle__in=my_public_circles, member=puser, active=True, approved=True).exists():
            return True

        # todo: friend's friend
        # might need to create another type of circles for friends' friends.

        return False

    def membership_queryset_loop(self):
        """
        Return the queryset of membership where the user is a active member of regardless of approval status.
        """
        return self.membership_set.filter(circle__type=Circle.Type.PERSONAL.value, active=True).exclude(circle__owner=self)

    def is_onboard(self):
        return self.has_info() and self.info.area and self.first_name
