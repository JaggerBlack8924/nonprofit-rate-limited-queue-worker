import unittest

from queue_worker import next_action


class QueueDecisionTest(unittest.TestCase):
    def test_receipt_job_becomes_receipt_action(self):
        job = {"id": "receipt-100", "kind": "donor_receipt"}
        self.assertEqual(next_action(job), "send_receipt")


if __name__ == "__main__":
    unittest.main()

