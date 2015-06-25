from django.contrib.auth.models import User
from django.db import models
from image_cropping import ImageCropField, ImageRatioField
from localflavor.us.models import PhoneNumberField
from django.core import checks
from circle.models import Membership, Circle
from p2 import settings
from s2c2.utils import auto_user_name


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

    # note: use User.active instead.
    # False:     the user has setup a password, and is able to login (not necessarily filled out anything)
    # True:    just created a user stub with email only.
    # stub = models.BooleanField()

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class PUser(User):
    """
    This is the proxy class for User instead of using monkey patch.
    """

    class Meta:
        proxy = True

    @staticmethod
    def from_user(user):
        return PUser.objects.get(pk=user.id)

    def get_area(self):
        try:
            return self.info.area
        except Info.DoesNotExist:
            return None

    def join(self, circle):
        membership, created = Membership.objects.update_or_create(member=self, circle=circle, defaults={'active': True})
        return membership

    # a person could have multiple personal list based on area.
    def get_personal_circle(self, area=None):
        if area is None:
            area = self.get_area()
        circle, created = Circle.objects.get_or_create(type=Circle.Type.PERSONAL.value, owner=self, area=area, defaults={
            'name': 'personal'
        })
        return circle

    @staticmethod
    def create_stub(email):
        """
        Create a new "stub" user
        :return: the created puser object
        """

        user = PUser()
        user.username = auto_user_name(email)
        user.email = email
        user.set_unusable_password()
        user.is_active = False
        user.save()
        return user

    @staticmethod
    def get_or_create(email):
        try:
            puser = PUser.objects.get(email=email)
            return puser
        except PUser.DoesNotExist:
            return PUser.create_stub(email)

    @staticmethod
    def get_by_email(email):
        return PUser.objects.get(email=email)

    def has_info(self):
        try:
            self.info
            return True
        except Info.DoesNotExist:
            return False

    def has_picture(self):
        return self.has_info() and self.info.picture_original and self.info.picture_cropping


site_admin_user = PUser.get_or_create(settings.DEFAULT_FROM_EMAIL)
