import logging
from django.core.management import BaseCommand
from django.utils import timezone
from contract.algorithms import L2Recommender
from contract.models import Contract, Match


class Command(BaseCommand):
    help = 'Update active contracts and their matches.'

    def handle(self, *args, **options):
        qs = Contract.objects.filter(status=Contract.Status.ACTIVE.value, event_start__gte=timezone.now())
        logging.info('Total active contracts to handle: %s' % qs.count())
        recommender = L2Recommender()
        for contract in qs:
            recommender.recommend(contract)
            # if there are new matches not engaged, engage them
            for match in Match.objects.filter(contract=contract, status=Match.Status.INITIALIZED.value):
                match.engage()