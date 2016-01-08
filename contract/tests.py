from datetime import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from contract.models import Contract
from p2.utils import TestEnvMixin
from puser.models import PUser


class ContractTest(TestEnvMixin, TestCase):

    def test_basic(self):
        u = PUser.get_by_email('test@servuno.com')
        contract = Contract.objects.create(initiate_user=u, area=u.info.area, price=30, event_start=make_aware(datetime(2015, 1, 1, 13, 0, 0)), event_end=make_aware(datetime(2015, 1, 1, 14, 30, 0)))
        self.assertEqual(20, contract.hourly_rate())
