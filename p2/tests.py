# Create your tests here.
from django.test import SimpleTestCase

from p2.utils import RelationshipType


class TestUtils(SimpleTestCase):

    def test_relationship_type(self):
        self.assertEqual(5, RelationshipType.FRIEND.value)
        self.assertEqual('Friend', RelationshipType.FRIEND.label)
        self.assertEqual('FRIEND', RelationshipType.FRIEND.name)
        self.assertNotEqual('Friend', RelationshipType.FRIEND.name)
        self.assertEqual('KID_FRIEND', RelationshipType.KID_FRIEND.name)

        self.assertEqual('5,1', RelationshipType.to_db([RelationshipType.FRIEND, RelationshipType.DIRECT_FAMILY]))
        self.assertEqual([RelationshipType.FRIEND, RelationshipType.DIRECT_FAMILY], RelationshipType.from_db('5,1'))
