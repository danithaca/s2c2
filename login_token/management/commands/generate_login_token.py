import logging

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from login_token.models import Token


class Command(BaseCommand):
    help = 'Generate link tokens for all active users who do not have one.'

    def handle(self, *args, **options):
        user_model = get_user_model()
        qs = user_model.objects.filter(is_active=True).exclude(token__isnull=False)
        logging.info("Process users: %s" % qs.count())
        for user in qs:
            Token.generate(user)
