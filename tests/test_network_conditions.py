"""Unit tests for the Feature 3 network condition simulator."""

import unittest

from src.network_conditions import NetworkConditions


class NetworkConditionsTests(unittest.TestCase):
    def setUp(self):
        self.sleeps = []
        self.no_sleep = self.sleeps.append

    def test_zero_impairment_delivers_without_delay(self):
        conditions = NetworkConditions(sleep_func=self.no_sleep)
        result = conditions.apply("message")
        self.assertTrue(result.delivered)
        self.assertEqual(result.delay_ms, 0.0)
        self.assertEqual(self.sleeps, [])

    def test_full_loss_drops_every_message_without_sleeping(self):
        conditions = NetworkConditions(loss_rate=1, sleep_func=self.no_sleep)
        results = [conditions.apply(number) for number in range(5)]
        self.assertTrue(all(not result.delivered for result in results))
        self.assertEqual(self.sleeps, [])

    def test_fixed_seed_is_deterministic(self):
        first = NetworkConditions(20, 5, 0.3, seed=7, sleep_func=self.no_sleep)
        second = NetworkConditions(20, 5, 0.3, seed=7, sleep_func=self.no_sleep)
        first_results = [first.apply(number) for number in range(10)]
        second_results = [second.apply(number) for number in range(10)]
        self.assertEqual(first_results, second_results)

    def test_jitter_never_produces_negative_delay(self):
        conditions = NetworkConditions(0, 100, seed=3, sleep_func=self.no_sleep)
        results = [conditions.apply(number) for number in range(100)]
        self.assertTrue(all(result.delay_ms >= 0 for result in results))

    def test_accounting_matches_delivery_results(self):
        conditions = NetworkConditions(loss_rate=0.4, seed=4, sleep_func=self.no_sleep)
        results = [conditions.apply(number) for number in range(10)]
        delivered = sum(result.delivered for result in results)
        dropped = sum(not result.delivered for result in results)
        self.assertEqual(delivered + dropped, 10)
        self.assertEqual(dropped, 10 - delivered)

    def test_invalid_configuration_is_rejected(self):
        with self.assertRaises(ValueError):
            NetworkConditions(latency_ms=-1)
        with self.assertRaises(ValueError):
            NetworkConditions(jitter_ms=-1)
        with self.assertRaises(ValueError):
            NetworkConditions(loss_rate=1.1)


if __name__ == "__main__":
    unittest.main()
