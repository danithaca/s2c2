from datetime import time
from django.test import TestCase
from slot.models import HalfHourTime


class HalfHourTimeTest(TestCase):

    def test_create(self):
        s = time(hour=0, minute=0)
        s1 = time(hour=0, minute=30)
        e = time(hour=23, minute=30)

        t = HalfHourTime(s)
        self.assertEqual(s, t.start_time)
        self.assertEqual(s1, t.end_time)

        self.assertEqual('12:00AM ~ 12:30AM', str(t))

        self.assertEqual(e, HalfHourTime.prev(s))
        self.assertEqual(s, HalfHourTime.next(e))

        interval = HalfHourTime.interval(time(hour=4, minute=0), time(hour=7, minute=30))
        self.assertEqual(7, len(interval))
        self.assertEqual(time(hour=4, minute=0), interval[0])
        self.assertEqual(time(hour=7, minute=0), interval[-1])

        self.assertRaises(AssertionError, HalfHourTime.interval, s, s)
        self.assertRaises(AssertionError, HalfHourTime.interval, e, s)