import logging

from django.core.management import BaseCommand

from login_token.models import Token
from login_token.conf import settings


class Command(BaseCommand):
    help = 'Replace all existing login tokens with length: %d' % settings.LOGIN_TOKEN_LENGTH

    def handle(self, *args, **options):
        qs = Token.objects.all()
        logging.info("Process tokens: %s" % qs.count())
        for token in qs:
            token.new_token()
