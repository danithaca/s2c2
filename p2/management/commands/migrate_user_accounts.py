import logging

from account.models import EmailAddress
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX
from django.core.management import BaseCommand
from django.db.models import F, Q

from circle.models import Membership, Circle
from login_token.models import Token
from puser.models import PUser, Info, Waiting
from django.db import connection


class Command(BaseCommand):
    help = 'Check the consistency of user accounts through all the code changes.'

    def handle(self, *args, **options):
        logging.root.setLevel(logging.INFO)

        ##### check duplicate emails
        cursor = connection.cursor()
        cursor.execute('SELECT email, COUNT(*) FROM ' + PUser._meta.db_table + ' GROUP BY email HAVING COUNT(*) > 1')
        rows = cursor.fetchall()
        logging.warning('Duplicate user email exits: %s' % len(rows))

        ##### info of total and inactive users
        inactive_users_qs = PUser.objects.filter(is_active=False)
        logging.info('Total # of users: %d' % PUser.objects.all().count())
        logging.info('Inactive users: %d' % inactive_users_qs.count())

        ##### handle missing EmailAddress objects.
        to_add_users = PUser.objects.exclude(emailaddress__email=F('email')).filter(is_active=True)
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

        ##### handle missing Info
        missing_info_users = PUser.objects.filter(info__isnull=True)
        logging.info('Total users to add Info: %s' % missing_info_users.count())
        for user in missing_info_users:
            # try:
            #     user.info
            #     assert False, "user info exists: %s" % u.username
            # except Info.DoesNotExist:
            #     pass
            # membership = Membership.objects.filter(member=u, circle__type=Circle.Type.PERSONAL.value).order_by('-updated').first()
            # if membership:
            #     Info.objects.create(user=u, area=membership.circle.area)
            Info.objects.create(user=user, registered=False)

        ##### handle Pre-registered users
        # note: only set registered=False. we don't set registered=True if info is complete.
        logging.info('Pre-registered users: %d', PUser.objects.filter(info__registered=False).count())
        to_pre_registered_users = PUser.objects.filter(Q(password__startswith=UNUSABLE_PASSWORD_PREFIX) | Q(first_name='') | Q(last_name='')).exclude(info__registered=False)
        logging.info('# of users to mark as pre-registered: %d', to_pre_registered_users.count())
        # this doesn't work on mysql
        # Info.objects.filter(user__in=to_pre_registered_users).update(registered=False)
        Info.objects.filter(user__id__in=[user.id for user in to_pre_registered_users]).update(registered=False)

        #### add login token to pre-registered users
        token_users = PUser.objects.filter(is_active=True, info__registered=False, token__isnull=True)
        logging.info('# of users to add login_token: %d' % token_users.count())
        for user in token_users:
            Token.generate(user)

        ##### handle inactive user: use login_token instead
        # add_token_users = PUser.objects.filter(is_active=False).exclude(token__isnull=False)
        # logging.info('Total inactive users to switch to LoginToken: %d' % add_token_users.count())
        # for user in add_token_users:
        #     Token.generate(user, is_user_registered=False)
        #     user.is_active = True
        #     user.save()

        #### associate users to waiting list
        waiting_list = Waiting.objects.filter(user__isnull=True)
        logging.info('Waiting list w/o users: %d' % waiting_list.count())
        for waiting_email in waiting_list:
            try:
                email_address = EmailAddress.objects.get(email=waiting_email.email)
                waiting_email.user = email_address.user.to_puser()
                waiting_email.save()
            except EmailAddress.DoesNotExist:
                pass
