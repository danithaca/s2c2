from django.test import TestCase

from puser.models import PUser


class PUserTest(TestCase):
    def test_trusted(self):
        u1 = PUser.get_by_email('test@servuno.com')
        u2 = PUser.get_by_email('test1@servuno.com')
        self.assertTrue(u1.trusted(u2))
        u3 = PUser.get_by_email('mrzhou@umich.edu')
        self.assertFalse(u1.trusted(u3))