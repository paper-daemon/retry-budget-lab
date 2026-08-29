import unittest
from retry_budget_lab import schedule, metrics, analyze

class T(unittest.TestCase):
    def test_schedule_and_metrics(self):
        s=schedule(4,1,2,30,0)
        self.assertEqual([x['delay_before'] for x in s],[0.0,1,2,4])
        m=metrics(3,.5)
        self.assertAlmostEqual(m['expected_requests_per_job'],1.75)
        self.assertAlmostEqual(m['success_probability'],.875)
        r=analyze(3,1,2,30,0,.5,10,5)
        self.assertEqual(r['max_concurrent_requests_if_all_retry'],30)
