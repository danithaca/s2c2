from django.core.management import BaseCommand
from contract.models import Contract


class Command(BaseCommand):
    help = 'Arbitrary script run.'

    def handle(self, *args, **options):
        contract = Contract.objects.get(pk=3)
        # contract.status = Contract.Status.INITIATED.value
        # contract.activate()

        for m in contract.match_set.all():

            print(m.target_user.email, '', Contract.Status(m.status))
            for c in m.circles.all():
                print(c.name)