import unittest

from bigdata.run_streaming_pipeline import live_cycle_delay


class LiveCycleTimingTests(unittest.TestCase):
    def test_fast_scan_uses_remaining_interval(self):
        self.assertEqual(live_cycle_delay(60, 12), 48)

    def test_slow_scan_retains_cooldown(self):
        self.assertEqual(live_cycle_delay(60, 53), 30)
        self.assertEqual(live_cycle_delay(60, 90), 30)

    def test_short_explicit_interval_remains_a_cooldown(self):
        self.assertEqual(live_cycle_delay(5, 8), 5)
