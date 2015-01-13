from datetime import time, date
from django.test import TestCase, SimpleTestCase
from slot.models import HalfHourTime, DayToken, DayTokenField, TimeToken


class HalfHourTimeTest(SimpleTestCase):

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


class DayTokenTest(SimpleTestCase):

    def test(self):
        dt0 = DayToken(date(1900, 1, 2))
        dt1 = DayToken.from_token('1')
        self.assertTrue(dt1.is_regular())
        self.assertEqual(dt0, dt1)
        self.assertEqual('1', dt1.get_token())

        self.assertRaises(ValueError, DayToken.from_token, '10')
        self.assertRaises(ValueError, DayToken.from_token, '7')
        self.assertRaises(ValueError, DayToken.from_token, '-1')
        self.assertRaises(ValueError, DayToken.from_token, '121212')

        dt2 = DayToken.from_token('20120101')
        self.assertEqual(DayToken(date(2012, 1, 1)), dt2)
        self.assertEqual('20120101', dt2.get_token())

        self.assertRaises(AssertionError, DayToken, '0')

        self.assertRaises(ValueError, DayToken.from_token, '20121301')
        self.assertRaises(ValueError, DayToken.from_token, '20121140')
        self.assertRaises(ValueError, DayToken.from_token, '99990101')

    # def test_field(self):
    #     df1 = DayTokenField()


class TimeTokenTest(SimpleTestCase):
    def test(self):
        tt1 = TimeToken(time(0, 0))
        self.assertEqual(time(0, 0), tt1.value)
        self.assertEqual('0000', tt1.get_token())

        self.assertEqual(TimeToken(time(13, 30)), TimeToken.from_token('1330'))
        self.assertRaises(ValueError, TimeToken.from_token, '1331')
        self.assertRaises(ValueError, TimeToken.from_token, '13')
        self.assertRaises(ValueError, TimeToken.from_token, '0')

        self.assertFalse(TimeToken.check_time(time(4, 1)))
        self.assertTrue(TimeToken.check_time(time(4, 0)))

        self.assertEqual(time(5, 0), TimeToken.next(time(4, 30)))
        self.assertEqual(time(0, 0), TimeToken.next(time(23, 30)))
        self.assertEqual(time(23, 30), TimeToken.prev(time(0, 0)))
        self.assertEqual(time(23, 0), TimeToken.prev(time(23, 30)))

        interval = TimeToken.interval(time(4, 0), time(7, 30))
        self.assertEqual(7, len(interval))
        self.assertEqual(time(4, 0), interval[0])
        self.assertEqual(time(7, 0), interval[-1])