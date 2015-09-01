from account.models import Account, EmailAddress
from account.signals import password_changed
from account.views import PasswordResetTokenView
from django.contrib.auth.models import User, AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q, F
from django.dispatch import receiver
from django.utils import timezone
from image_cropping import ImageCropField, ImageRatioField
from localflavor.us.models import PhoneNumberField
from django.core import checks
from circle.models import Membership, Circle
from contract.models import Contract, Match, Engagement
from django.conf import settings
from login_token.models import Token
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

    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
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


# class PUser(AbstractUser):
class PUser(User):
    """
    This is the proxy class for User instead of using monkey patch.
    """

    class Meta():
        proxy = True
        # db_table = 'auth_user'

    # class AlreadyExists(Exception):
    #     pass

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
        assert isinstance(user, User)
        if isinstance(user, PUser):
            return user
        else:
            return PUser.objects.get(pk=user.id)

    def get_area(self):
        try:
            return self.info.area
        except Info.DoesNotExist:
            return None

    # a person could have multiple personal list based on area.
    def get_personal_circle(self, area=None):
        if area is None:
            area = self.get_area()
        circle, created = Circle.objects.get_or_create(type=Circle.Type.PERSONAL.value, owner=self, area=area, defaults={
            'name': 'personal'
        })
        return circle

    @staticmethod
    def create(email, password=None, dummy=True, area=None):
        # supposedly to use in the referral creation phase and not the full process of user signup. if not use in referral creation
        # neglected: 1. signup_code, 2.email verification (some cases email might have already been verified), 3. email confirmation requirement, 4. login
        assert not PUser.objects.filter(email=email).exists() and not EmailAddress.objects.filter(email=email).exists()

        user = PUser()
        user.username = auto_user_name(email)
        user.email = email
        if not dummy and password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        # make sure user is active
        user.is_active = True

        # we want to handle Account/EmailAddress creation manually, because signals have some
        user._disable_account_creation = True
        user.save()

        # now create Account/EmailAddress
        Account.create(user=user)

        # create Info(?) and login token.
        if dummy:
            Token.generate(user, is_user_registered=False)

        if area:
            Info.objects.create(user=user, area=area)

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

    def engagement_queryset(self):
        return Contract.objects.filter(Q(initiate_user=self) | Q(match__target_user=self)).distinct()

    def engagement_list(self, extra_query = lambda qs: qs):
        list_engagement = []
        for contract in extra_query(self.engagement_queryset()):
            if contract.initiate_user == self:
                list_engagement.append(Engagement.from_contract(contract))
            else:
                try:
                    match = Match.objects.get(contract=contract, target_user=self)
                    list_engagement.append(Engagement.from_match(match))
                except:
                    continue
        return list_engagement

    def engagement_headline(self):
        # headline logic:
        # show the most recent one that needs my attention:
        # 1. if i'm the client, then always show if it's initiated, active or confirmed.
        # 2. if i'm the server, then show when i'm confirmed or i haven't responded.
        # use "id" as the 2nd "order by" for consistent ordering.
        engagement_list = self.engagement_list(lambda qs: qs.filter((Q(initiate_user=self) & Q(status__in=(Contract.Status.INITIATED.value, Contract.Status.ACTIVE.value, Contract.Status.CONFIRMED.value))) | (Q(match__target_user=self) & (Q(match__status__in=(Match.Status.ENGAGED.value,)) | Q(match=F('confirmed_match'))))).filter(event_start__gt=timezone.now()).order_by('event_start', 'id')[:1])
        if engagement_list:
            return engagement_list[0]
        else:
            # if not found, then return None
            return None

    def count_served(self, client):
        """
        Count how many times the current puser (as "server") has served the client.
        """
        assert isinstance(client, User)     # PUser is also an instance of user.
        return Contract.objects.filter(confirmed_match__target_user=self, initiate_user=client, status=Contract.Status.SUCCESSFUL.value).count()

    def count_favors(self, client):
        """
        Count how many times the current puser (as "server") has served the client as favors.
        """
        assert isinstance(client, User)     # PUser is also an instance of user.
        count = 0
        for contract in Contract.objects.filter(confirmed_match__target_user=self, initiate_user=client, status=Contract.Status.SUCCESSFUL.value):
            if contract.is_favor():
                count += 1
        return count

    def get_login_token(self, force=False):
        try:
            token = self.token
            return token.token
        except Token.DoesNotExist:
            if force:
                token = Token.generate(user=self)
                return token.token
            else:
                return None

    ######## methods that check user's status #########
    # is_active: from django system. inactive means the user cannot login (perhaps a spam user), and cannot use the site.
    # is_registered: shows whether the user is signed up by other people, or has been through the sign up process. not-registered user doesn't have a valid password
    # is_onboard: user has been through the onboarding process and (should) added first/last name and area.
    # is_onboard includes is_registered. is_active is orthogonal.

    def is_onboard(self):
        return self.has_info() and self.info.area and self.first_name

    def is_registered(self):
        try:
            token = self.token
            return token.is_user_registered
        except Token.DoesNotExist:
            # no token by default means already registered.
            return True


# @receiver(password_changed, sender=PasswordResetTokenView)
# @receiver(password_changed, sender=ChangePasswordView)
@receiver(password_changed)
def handle_pre_registered_user_after_password_change(sender, user, **kwargs):
    try:
        token = user.token
        if not token.is_user_registered:
            token.is_user_registered = True
            token.save()
    except Token.DoesNotExist:
        pass

@receiver(password_changed, sender=PasswordResetTokenView)
def verify_email_after_password_reset(sender, user, **kwargs):
    EmailAddress.objects.filter(user=user, email=user.email, verified=False).update(verified=True)
