import logging
from datetime import timedelta
from django.core.management import BaseCommand
from django.utils import timezone
from contract.algorithms import L2Recommender
from contract.models import Contract, Match


class Command(BaseCommand):
    help = 'Update expired contracts and mark them as successful, or purge them for archival purposes.'

    def handle(self, *args, **options):
        # after 7 days, if still not marked as successful, we'll mark as successful.
        cutoff = timezone.now() - timedelta(days=7)
        qs = Contract.objects.filter(status=Contract.Status.CONFIRMED.value, event_end__lt=cutoff)
        logging.info('Total expired contracts to mark as successful: %s' % qs.count())
        for contract in qs:
            contract.status = Contract.Status.SUCCESSFUL.value
            contract.save()
