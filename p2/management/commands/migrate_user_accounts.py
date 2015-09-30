import logging

from account.models import EmailAddress
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db.models import F

from circle.models import Membership, Circle
from login_token.models import Token
from puser.models import PUser, Info


class Command(BaseCommand):
    help = 'Support s2c2 users to be with p2 users'

    def handle(self, *args, **options):
        logging.root.setLevel(logging.INFO)
        ######### handle email addresses
        to_add_users = User.objects.exclude(emailaddress__email=F('email')).filter(is_active=True)
        logging.info('Total users to add EmailAddress: %s' % to_add_users.count())
        for user in to_add_users:
            EmailAddress.objects.add_email(user, user.email)

        # now all user emails are in EmailAddress
        to_set_primary = EmailAddress.objects.filter(primary=False, user__email=F('email'))
        logging.info('Emails to set as primary: %s' % to_set_primary.count())
        for email_address in to_set_primary:
            old_primary = EmailAddress.objects.get_primary(email_address.user)
            if old_primary:
                old_primary.primary = False
                old_primary.save()
            email_address.primary = True
            email_address.save()

        ######### handle inactive user: use login_token instead
        qs = PUser.objects.filter(is_active=False).exclude(token__isnull=False)
        logging.info('Total inactive users to switch to LoginToken: %d' % qs.count())
        for u in qs:
            Token.generate(u, is_user_registered=False)
            u.is_active = True
            u.save()

        ######## handle info #######
        qs = PUser.objects.filter(is_staff=False).filter(info__isnull=True).filter(membership__isnull=False)
        for u in qs:
            try:
                u.info
                assert False, "user info exists: %s" % u.username
            except Info.DoesNotExist:
                pass
            membership = Membership.objects.filter(member=u, circle__type=Circle.Type.PERSONAL.value).order_by('-updated').first()
            if membership:
                Info.objects.create(user=u, area=membership.circle.area)

