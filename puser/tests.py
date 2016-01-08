from django.test import TestCase

from p2.utils import TestEnvMixin
from puser.models import PUser


class PUserTest(TestEnvMixin, TestCase):
    def test_trusted(self):
        u = PUser.get_by_email('test@servuno.com')
        u1 = PUser.get_by_email('test1@servuno.com')
        u2 = PUser.get_by_email('test2@servuno.com')
        self.assertTrue(u.is_user_trusted(u1))
        self.assertTrue(u1.is_user_trusted(u))
        self.assertFalse(u1.is_user_trusted(u2))