from datetime import timedelta
from enum import Enum

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
from localflavor.us.models import PhoneNumberField, USStateField

from django.core import checks
from django.conf import settings
from sitetree.models import TreeItemBase

from circle.models import Membership, Circle, ParentCircle, UserConnection

from contract.models import Contract, Match, Engagement
from login_token.models import Token
from p2.utils import auto_user_name


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


class UserRole(Enum):
    PARENT = 7
    SITTER = 8


class Info(models.Model):
    """
    The extended field for p2 Users.
    Authentication/authorization would be handled by user_account.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    address = models.CharField(max_length=200, blank=True)
    phone = PhoneNumberField(blank=True)
    phone_backup = PhoneNumberField(blank=True, help_text='Phone number added by other people')
    note = models.TextField(blank=True)
    homepage = models.URLField(blank=True)
    role = models.PositiveSmallIntegerField(choices=[(t.value, t.name.capitalize()) for t in UserRole], blank=True, null=True)

    picture_original = ImageCropField(upload_to='picture', blank=True, null=True)
    picture_cropping = ImageRatioField('picture_original', '200x200')

    # user's home area. it doesn't necessarily mean the user will request/respond to this area only.
    area = models.ForeignKey(Area, default=1)

    # whether this user is pre-registered, or registered.
    registered = models.BooleanField(default=True)

    # note: use User.is_active instead.
    # False:     the user has setup a password, and is able to login (not necessarily filled out anything)
    # True:    just created a user stub with email only.
    # stub = models.BooleanField()

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @staticmethod
    def get_or_create_for_user(user):
        assert isinstance(user, User)
        info, created = Info.objects.get_or_create(user=user)
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

    def has_area(self):
        try:
            if self.info.area is not None:
                return True
        except Info.DoesNotExist:
            pass
        return False

    def get_area(self):
        # try:
        #     return self.info.area
        # except Info.DoesNotExist:
        #     return None
        # raise exception if it doesn't have one.
        return self.info.area

    # a person could have multiple personal list based on area.
    def get_personal_circle(self, area=None):
        if area is None:
            area = self.get_area()
        circle, created = Circle.objects.get_or_create(type=Circle.Type.PERSONAL.value, owner=self, area=area, defaults={
            'name': '%s:personal:%d' % (self.username, area.id)
        })
        return circle

    def my_circle(self, type, area=None):
        """
        Return the user's circle, cast to proxy model if exists.
        """
        assert isinstance(type, Circle.Type)
        if area is None:
            area = self.get_area()
        default_name = '%s:%s:%d' % (self.username, type.name.lower(), area.id)

        # make sure to use the proxy class
        circle_class = Circle
        if type == Circle.Type.PARENT:
            circle_class = ParentCircle
        circle, created = circle_class.objects.get_or_create(type=type.value, owner=self, area=area, defaults={
            'name': default_name
        })
        return circle

    def get_tag_circle_set(self, area=None):
        if area is None:
            area = self.get_area()
        membership = self.membership_set.filter(circle__type=Circle.Type.TAG.value, active=True, approved=True, circle__area=area)
        return set([m.circle for m in membership])

    # public circles the user joined (and approved)
    def get_public_circle_set(self, area=None):
        if area is None:
            area = self.get_area()
        membership = self.membership_set.filter(circle__type=Circle.Type.PUBLIC.value, active=True, approved=True, circle__area=area)
        return set([m.circle for m in membership])

    def get_agency_circle_set(self, area=None):
        if area is None:
            area = self.get_area()
        # we don't care about "approve" here.
        membership = self.membership_set.filter(circle__type=Circle.Type.AGENCY.value, active=True, type=Membership.Type.PARTIAL.value, circle__area=area)
        return set([m.circle for m in membership])

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

        # now create Account/EmailAddress. "EmailAddress" is created in Account.create()
        Account.create(user=user)

        registered = False if dummy else True
        if area:
            info = Info.objects.create(user=user, registered=registered, area=area)
        else:
            info = Info.objects.create(user=user, registered=registered)

        # create Info(?) and login token.
        if dummy:
            Token.generate(user, is_user_registered=False)

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

        # trust someone in my personal/parent/sitter circle
        my_personal_circles = Circle.objects.filter(type__in=(Circle.Type.PERSONAL.value, Circle.Type.PARENT.value, Circle.Type.SITTER.value), owner=self)
        if Membership.objects.filter(circle__in=my_personal_circles, member=puser, active=True).exists():
            return True

        # trust someone i'm part of her personal/parent/sitter circle which I approved
        their_personal_circles = Circle.objects.filter(type__in=(Circle.Type.PERSONAL.value, Circle.Type.PARENT.value, Circle.Type.SITTER.value), owner=puser)
        if Membership.objects.filter(circle__in=their_personal_circles, member=self, approved=True).exists():
            return True

        # trust someone in the public/TAG circles where I'm a member of.
        my_public_circles = Circle.objects.filter(type__in=(Circle.Type.PUBLIC.value, Circle.Type.TAG.value), membership__member=self, membership__active=True, membership__approved=True)
        if Membership.objects.filter(circle__in=my_public_circles, member=puser, active=True, approved=True).exists():
            return True

        # trust anyone who has a "match" object within +/1 7days window
        # this is mostly for agency users.
        window_start = timezone.now() - timedelta(days=7)
        window_end = timezone.now() + timedelta(days=7)
        if Match.objects.filter(target_user=self, contract__initiate_user=puser, contract__event_end__lt=window_end, contract__event_start__gt=window_start).exists():
            return True
        if Match.objects.filter(target_user=puser, contract__initiate_user=self, contract__event_end__lt=window_end, contract__event_start__gt=window_start).exists():
            return True

        # trust anyone who have a upcoming confirmed match regardless of time
        if Contract.objects.filter(initiate_user=self, confirmed_match__target_user=puser, status=Contract.Status.CONFIRMED.value, event_start__gt=timezone.now()).exists():
            return True
        if Contract.objects.filter(initiate_user=puser, confirmed_match__target_user=self, status=Contract.Status.CONFIRMED.value, event_start__gt=timezone.now()).exists():
            return True

        # todo: friend's friend
        # might need to create another type of circles for friends' friends.

        return False

    def membership_queryset_loop(self):
        """
        Return the queryset of membership where the user is a active member of regardless of approval status.
        """
        return self.membership_set.filter(circle__type=Circle.Type.PERSONAL.value, active=True, circle__area=self.get_area()).exclude(circle__owner=self)

    def membership_queryset_public(self):
        return self.membership_set.filter(circle__type=Circle.Type.PUBILC.value, active=True, approved=True, circle__area=self.get_area())

    def engagement_queryset(self):
        return Contract.objects.filter(Q(initiate_user=self) | Q(match__target_user=self)).distinct()

    def engagement_list(self, extra_query=lambda qs: qs):
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
        engagement_list = self.engagement_list(lambda qs: qs.filter((Q(initiate_user=self) & Q(status__in=(Contract.Status.INITIATED.value, Contract.Status.ACTIVE.value, Contract.Status.CONFIRMED.value))) | (Q(match__target_user=self) & (Q(match__status__in=(Match.Status.ENGAGED.value,)) | Q(match=F('confirmed_match'))))).filter(event_start__gt=timezone.now(), event_end__lt=timezone.now() + timedelta(days=60)).order_by('event_start', 'id')[:1])
        if engagement_list:
            return engagement_list[0]
        else:
            # if not found, then return None
            return None

    def engagement_favors(self):
        results = []
        # we filter by price=0 for now, which might change later depending on what counts as favors.
        engagement_list = self.engagement_list(extra_query=lambda qs: qs.filter(price=0, event_end__lt=timezone.now(), status=Contract.Status.SUCCESSFUL.value))
        for engagement in engagement_list:
            if engagement.contract.is_favor() and (engagement.is_main_contract() or engagement.is_match_confirmed()):
                results.append(engagement)
        return results

    def contract_feedback_needed_queryset(self):
        return Contract.objects.filter(initiate_user=self, status=Contract.Status.CONFIRMED.value, confirmed_match__isnull=False, event_end__lt=timezone.now())

    def count_served(self, client):
        """
        Count how many times the current puser (as "server") has served the client.
        """
        assert isinstance(client, User)     # PUser is also an instance of user.
        return Contract.objects.filter(status=Contract.Status.SUCCESSFUL.value).filter(Q(confirmed_match__target_user=self, initiate_user=client, reversed=False) | Q(initiate_user=self, confirmed_match__target_user=client, reversed=True)).count()

    def count_favors(self, client):
        """
        Count how many times the current puser (as "server") has served the client as favors.
        """
        assert isinstance(client, User)     # PUser is also an instance of user.
        count = 0
        for contract in Contract.objects.filter(status=Contract.Status.SUCCESSFUL.value).filter(Q(confirmed_match__target_user=self, initiate_user=client, reversed=False) | Q(initiate_user=self, confirmed_match__target_user=client, reversed=True)):
            if contract.is_favor():
                count += 1
        return count

    def count_favors_all(self):
        # count = 0
        # for contract in Contract.objects.filter(confirmed_match__target_user=self, status=Contract.Status.SUCCESSFUL.value):
        #     if contract.is_favor():
        #         count += 1

        # TODO: this need to think thru. for a parent (not sitter), even paid job could be a favor.
        return Contract.objects.filter(status=Contract.Status.SUCCESSFUL.value).filter(Q(confirmed_match__target_user=self, reversed=False) | Q(initiate_user=self, reversed=True)).count()

    def count_interactions(self, target_user):
        return Contract.objects.filter(status=Contract.Status.SUCCESSFUL.value).filter(Q(confirmed_match__target_user=self, initiate_user=target_user) | Q(initiate_user=self, confirmed_match__target_user=target_user)).count()

    def get_level(self):
        count = self.count_favors_all()
        levels = [
            (0, 0, 'Newborn Angel'),
            (1, 1, 'Baby Angel'),
            (2, 3, 'Toddler Angel'),
            (3, 7, 'Teenage Angel'),
            (4, 15, 'Young Angel'),
            (5, 50, 'Arch Angel'),
        ]
        next_levels = levels[1:] + [(6, 1000, 'God')]
        for this_level, next_level in zip(levels, next_levels):
            if this_level[1] <= count < next_level[1]:
                break
        return {
            'level': this_level[0],
            'title': this_level[2],
            'count': count,
            'next_level': next_level[0],
            'next_level_title': next_level[2],
            'next_level_count': next_level[1],
            'next_level_more': next_level[1] - count,
        }

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

    def get_shared_connection(self, target_user):
        # shared connection: 1) directly in my personal network (parent/sitter), 2) in my parents friends' network (both parents and sitters).
        # potentially will have the "tag" shared connection
        # get all users (for circle owners) in current area
        area = self.get_area()
        my_parent_list = [self] + list(PUser.objects.filter(membership__active=True, membership__approved=True, membership__circle__owner=self, membership__circle__type=Circle.Type.PARENT.value, membership__circle__area=area).distinct())
        # get all members who are in the personal circles of the previous parent list.
        membership_list = Membership.objects.filter(member=target_user, active=True, approved=True, circle__owner__in=my_parent_list, circle__type__in=(Circle.Type.PARENT.value, Circle.Type.SITTER.value), circle__area=area)
        return UserConnection(self, target_user, list(membership_list))

    ######## methods that check user's status #########
    # is_active: from django system. inactive means the user cannot login (perhaps a spam user), and cannot use the site.
    # 2015/11/2 update: is_onboard and is_registered is the same now. which means fullname/lastname/area/password is all set. Another thing other than that would be considered pre-registered
    # is_isolated: too few contacts. need to add more

    # this could be obsolete in favor of is_registered.
    def is_onboard(self):
        return self.is_registered()

    def is_registered(self):
        # use the management command to make sure the "registered" field is correct and consistent.
        if self.has_info() and self.info.registered:
            return True
        else:
            return False

    def is_isolated(self):
        # we count non-active/approved here.
        count_parent = Membership.objects.filter(circle__owner=self, circle__type=Circle.Type.PARENT.value, active=True, approved=True).count()
        count_sitter = Membership.objects.filter(circle__owner=self, circle__type=Circle.Type.SITTER.value, active=True, approved=True).count()
        if count_parent + count_sitter <= 3:
            return True
        else:
            return False

    def get_full_name(self):
        name = super().get_full_name()
        if not name:
            name = self.email
        return name


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


class MenuItem(TreeItemBase):
    fa_icon = models.CharField(help_text='Font awesome icon', blank=True, max_length=50)
    # css_id = models.CharField(help_text='CSS ID', blank=True, max_length=50)
    importance = models.SmallIntegerField(help_text='The importance of this item', choices=((0, 'Regular'), (1, 'Highlight'), (-1, 'Muted')), default=0)
