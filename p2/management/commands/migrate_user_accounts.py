import logging
from account.models import EmailAddress
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db.models import F


class Command(BaseCommand):
    help = 'Support s2c2 users to be with p2 users'

    def handle(self, *args, **options):
        to_add_users = User.objects.exclude(emailaddress__email=F('email'))
        logging.info('Total users to add: %s' % to_add_users.count())
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
