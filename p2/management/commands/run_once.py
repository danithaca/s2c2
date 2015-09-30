import json
import os
from pprint import pprint

from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Arbitrary script run.'

    def handle(self, *args, **options):
        # print('Running on the fly script.')
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

        # u = PUser.get_by_email('mrzhou@umich.edu')
        # Contract.objects.create(buyer=u, event_start=datetime.now(), event_end=datetime.now()+timedelta(hours=1), price=10, area=Area.objects.get(pk=1))
        # this should be automatically activated.
        # send_mail('test subject', 'test message', 'admin@servuno.com', ['admin@knowsun.com'], False)
        # for circle in Circle.objects.filter(type=Circle.Type.PERSONAL.value):
        #     circle.name = '%s:personal:%d' % (circle.owner.username, circle.area_id)
        #     circle.save()

        with open(os.path.join(settings.DATA_DIR, 'family_helper_crawl.json'), 'r') as f:
            data = json.load(f)
            table = {r['email']:r for r in data}
            pprint(table['ebedrick@umich.edu'])