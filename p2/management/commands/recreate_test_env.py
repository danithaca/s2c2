from django.core.management import BaseCommand
from p2.utils import recreate_test_env


class Command(BaseCommand):
    help = 'Recreate test environment.'

    def handle(self, *args, **options):
        if input('This will destroy existing test data. Continue? [y/n]: ') == 'y':
            recreate_test_env()
        else:
            print('Nothing is done.')