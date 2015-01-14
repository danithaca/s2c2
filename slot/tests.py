from datetime import time, date

from django.test import SimpleTestCase

from slot.models import DayToken, TimeToken



# class HalfHourTimeTest(SimpleTestCase):
#
#     def test_create(self):
#         s = time(hour=0, minute=0)
#         s1 = time(hour=0, minute=30)
#         e = time(hour=23, minute=30)
#
#         t = HalfHourTime(s)
#         self.assertEqual(s, t.start_time)
#         self.assertEqual(s1, t.end_time)
#
#         self.assertEqual('12:00AM ~ 12:30AM', str(t))
#
#         self.assertEqual(e, HalfHourTime.prev(s))
#         self.assertEqual(s, HalfHourTime.next(e))
#
#         interval = HalfHourTime.interval(time(hour=4, minute=0), time(hour=7, minute=30))
#         self.assertEqual(7, len(interval))
#         self.assertEqual(time(hour=4, minute=0), interval[0])
#         self.assertEqual(time(hour=7, minute=0), interval[-1])
#
#         self.assertRaises(AssertionError, HalfHourTime.interval, s, s)
#         self.assertRaises(AssertionError, HalfHourTime.interval, e, s)


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

        self.assertEqual(DayToken.from_token('0'), DayToken.from_token('6').next_day())
        self.assertEqual(DayToken.from_token('6'), DayToken.from_token('0').prev_day())
        self.assertEqual(DayToken.from_token('20140201'), DayToken.from_token('20140131').next_day())
        self.assertEqual(DayToken.from_token('20151205'), DayToken.from_token('20151206').prev_day())

        dt3 = DayToken.from_token('20151205')
        self.assertEqual(dt3.weekday(), dt3.next_week().weekday())
        self.assertEqual(dt3.weekday(), dt3.prev_week().weekday())
        self.assertEqual(DayToken.from_token('20151212'), dt3.next_week())
        self.assertEqual(DayToken.from_token('20151128'), dt3.prev_week())

        dt4 = DayToken.from_token('20150112')
        dt4_expand = dt4.expand_week()
        self.assertEqual(7, len(dt4_expand))
        self.assertEqual(DayToken(date(2015, 1, 18)), dt4_expand[-1])
        self.assertEqual(DayToken(date(2015, 1, 12)), dt4_expand[0])

        dt5 = DayToken(date(2015, 1, 18))
        dt5_expand = dt5.expand_week()
        self.assertEqual(DayToken(date(2015, 1, 18)), dt5_expand[-1])
        self.assertEqual(DayToken(date(2015, 1, 12)), dt5_expand[0])

        dt6 = DayToken(date(2015, 1, 13))
        dt6_expand = dt6.expand_week()
        self.assertEqual(DayToken(date(2015, 1, 18)), dt6_expand[-1])
        self.assertEqual(DayToken(date(2015, 1, 12)), dt6_expand[0])

    # def test_field(self):
    #     df1 = DayTokenField()


class TimeTokenTest(SimpleTestCase):
    def test(self):
        self.assertEqual(0, TimeToken._to_index(time(0)))
        self.assertEqual(47, TimeToken._to_index(time(23, 30)))
        self.assertEqual(2, TimeToken._to_index(time(1)))
        self.assertEqual(21, TimeToken._to_index(time(10, 30)))
        self.assertEqual(time(0), TimeToken._from_index(0))
        self.assertEqual(time(23, 30), TimeToken._from_index(47))
        self.assertEqual(time(1), TimeToken._from_index(2))
        self.assertEqual(time(10, 30), TimeToken._from_index(21))

        self.assertEqual(time(0), TimeToken._next(time(23, 30)))
        self.assertEqual(time(23, 30), TimeToken._prev(time(0)))

        tt1 = TimeToken(time(0, 0))
        self.assertEqual(time(0, 0), tt1.value)
        self.assertEqual('0000', tt1.get_token())

        self.assertEqual(TimeToken(time(13, 30)), TimeToken.from_token('1330'))
        self.assertRaises(ValueError, TimeToken.from_token, '1331')
        self.assertRaises(ValueError, TimeToken.from_token, '13')
        self.assertRaises(ValueError, TimeToken.from_token, '0')

        self.assertFalse(TimeToken.check_time(time(4, 1)))
        self.assertTrue(TimeToken.check_time(time(4, 0)))

        self.assertEqual(time(5, 0), TimeToken(time(4, 30)).get_next().value)
        self.assertEqual(time(0, 0), TimeToken(time(23, 30)).get_next().value)
        self.assertEqual(time(23, 30), TimeToken(time(0, 0)).get_prev().value)
        self.assertEqual(time(23, 0), TimeToken(time(23, 30)).get_prev().value)

        interval = TimeToken.interval(time(4, 0), time(7, 30))
        self.assertEqual(7, len(interval))
        self.assertEqual(time(4, 0), interval[0].value)
        self.assertEqual(time(7, 0), interval[-1].value)