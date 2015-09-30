from datetime import datetime

from django.test import TestCase

from contract.models import Contract
from location.models import Area
from puser.models import PUser


class ContractTest(TestCase):

    def test_basic(self):
        email = 'mrzhou@umich.edu'
        try:
            u1 = PUser.objects.get(email=email)
        except PUser.DoesNotExist:
            u1 = PUser.create(email, dummy=True)

        area, created = Area.objects.get_or_create(name='Ann Arbor', state='MI')
        contract = Contract(initiate_user=u1, event_start=datetime(2015, 1, 1, 13, 0, 0), event_end=datetime(2015, 1, 1, 14, 30, 0), price=30, area=area)
        contract.save()
        self.assertEqual(20, contract.hourly_rate())
