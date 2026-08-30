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
        self.assertEqual(r['max_concurrent_requests_if_all_retry'],10)
        self.assertEqual(r['worst_case_requests_for_concurrent_jobs'],30)

    def test_concurrency_is_not_multiplied_by_attempts(self):
        r=analyze(5,1,2,30,0,.5,7,5)
        self.assertEqual(r['max_concurrent_requests_if_all_retry'],7)
        self.assertEqual(r['worst_case_requests_for_concurrent_jobs'],35)

    def test_invalid_policy_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'attempts'):
            analyze(0,1,2,30,0,.5,10,5)
        with self.assertRaisesRegex(ValueError, 'jitter'):
            analyze(3,1,2,30,-.1,.5,10,5)
        with self.assertRaisesRegex(ValueError, 'success_prob'):
            analyze(3,1,2,30,0,1.2,10,5)
        with self.assertRaisesRegex(ValueError, 'timeout'):
            analyze(3,1,2,30,0,.5,10,-1)
        with self.assertRaisesRegex(ValueError, 'concurrency'):
            analyze(3,1,2,30,0,.5,0,5)
