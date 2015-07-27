import logging
from django.core.management import BaseCommand
from contract.models import Contract, Match

# we could use period command to send notification. but we aren't able to tell if reminder is already sent unless
# we track it in database. for now, we use celery to post reminder task with "eta".


class Command(BaseCommand):
    help = 'Send contract reminder before contract starts and after contract ends.'

    def handle(self, *args, **options):
        self.reminder_before_contract_starts()
        self.reminder_after_contract_ends()

    def reminder_before_contract_starts(self):
        pass

    def reminder_after_contract_ends(self):
        pass