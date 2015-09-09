import logging
from datetime import datetime
from django.utils import timezone
from django.core.management import BaseCommand
from circle.models import Membership
from contract.models import Contract
from puser.models import PUser


class Command(BaseCommand):
    help = 'Print out site stats for admin users.'

    def handle(self, *args, **options):
        cutoff = timezone.make_aware(datetime(year=2015, month=8, day=5))

        # registered users after 2015-8-5
        logging.info('Registered users: %d' % PUser.objects.filter(is_active=True, date_joined__gt=cutoff).exclude(email__icontains='servuno.com').exclude(token__is_user_registered=False).count())

        # preregistered users after 2015-8-5
        logging.info('Pre-registered users: %d' % PUser.objects.filter(is_active=True, date_joined__gt=cutoff).exclude(email__icontains='servuno.com').filter(token__is_user_registered=False).count())

        # total users after 2015-8-5
        logging.info('Total users: %d' % PUser.objects.filter(is_active=True, date_joined__gt=cutoff).exclude(email__icontains='servuno.com').count())

        # total users (non registered)
        logging.info('Total users (all time): %d' % PUser.objects.filter(is_active=True).exclude(email__icontains='servuno.com').count())

        # total number of contracts (post 2015-8-5)
        logging.info('Total contracts: %d' % Contract.objects.filter(created__gt=cutoff).exclude(initiate_user__email__icontains='servuno.com').count())

        # number of active contracts.
        logging.info('Active contracts: %d' % Contract.objects.filter(created__gt=cutoff, status=Contract.Status.ACTIVE.value, event_start__gt=timezone.now()).exclude(initiate_user__email__icontains='servuno.com').count())

        # unhandled memberships
        unhandled_membership = list(Membership.objects.filter(approved=False, active=True).exclude(member__email__icontains='servuno.com'))
        logging.info('Unhandled memberships: %d - %s' % (len(unhandled_membership), ','.join([str(m.id) for m in unhandled_membership])))
