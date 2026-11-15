import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import cron_explain as c


class Tests(unittest.TestCase):
    def test_fixed_time(self):
        self.assertEqual(c.explain("30 6 * * *"), "at 06:30")

    def test_every_minute(self):
        self.assertEqual(c.explain("* * * * *"), "every minute")

    def test_step_minutes(self):
        self.assertEqual(c.explain("*/15 * * * *"), "every 15 minutes")

    def test_weekdays(self):
        self.assertEqual(c.explain("0 9 * * mon-fri"),
                         "at 09:00, on Monday, Tuesday, Wednesday, Thursday and Friday")

    def test_month_and_day(self):
        self.assertEqual(c.explain("0 0 1 jan *"), "at 00:00, on day 1 of the month, in January")

    def test_alias(self):
        self.assertEqual(c.explain("@daily"), "at 00:00")

    def test_sunday_seven(self):
        self.assertEqual(c.parse_field("7", 4), [0])

    def test_range_step(self):
        self.assertEqual(c.parse_field("10-30/10", 0), [10, 20, 30])

    def test_bad_input(self):
        for bad in ["* * * *", "61 * * * *", "*/0 * * * *", "a * * * *"]:
            with self.assertRaises(ValueError):
                c.parse(bad)

    def test_next_runs(self):
        start = dt.datetime(2026, 1, 1, 8, 59)
        runs = c.next_runs("0 9 * * *", start, 2)
        self.assertEqual(runs, [dt.datetime(2026, 1, 1, 9, 0), dt.datetime(2026, 1, 2, 9, 0)])

    def test_next_runs_weekday(self):
        start = dt.datetime(2026, 1, 2, 12, 0)  # a Friday
        run = c.next_runs("0 9 * * mon", start, 1)[0]
        self.assertEqual(run, dt.datetime(2026, 1, 5, 9, 0))


if __name__ == "__main__":
    unittest.main()
