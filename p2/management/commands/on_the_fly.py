from celery.exceptions import TimeoutError
from django.core.management import BaseCommand
from contract.models import Contract
from contract.tasks import dummy
from location.models import Area
from puser.models import PUser
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Arbitrary script run.'

    def handle(self, *args, **options):
        # result = dummy.delay(3, 4)
        # print(result.ready())
        # try:
        #     print(result.get(timeout=3))
        # except TimeoutError:
        #     print('Timed out.')

        # contract = Contract.objects.get(pk=3)
        # contract.status = Contract.Status.INITIATED.value
        # contract.event_end = datetime.now()
        # contract.save()
        # contract.activate()
        #
        # for m in contract.match_set.all():
        #
        #     print(m.target_user.email, '', Contract.Status(m.status))
        #     for c in m.circles.all():
        #         print(c.name)

        u = PUser.get_by_email('mrzhou@umich.edu')
        Contract.objects.create(buyer=u, event_start=datetime.now(), event_end=datetime.now()+timedelta(hours=1), price=10, area=Area.objects.get(pk=1))
        # this should be automatically activated.