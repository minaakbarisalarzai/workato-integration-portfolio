import unittest
from reference.recovery_policy import MAX_BATCH_SIZE, evaluate


def job(**overrides):
    record = dict(job_id="job-1", recipe_id="recipe-A", status="failed",
                  error_category="connection_timeout", connection_health="healthy",
                  replay_safe=True, approved=True)
    record.update(overrides)
    return record


class RecoveryPolicyTests(unittest.TestCase):
    def test_eligible(self):
        result = evaluate([job()])
        self.assertEqual(result["suggested_count"], 1)
        self.assertTrue(result["suggested_batches"][0]["dry_run"])

    def test_not_connection_failure(self):
        self.assertEqual(evaluate([job(error_category="invalid_data")])["suggested_count"], 0)

    def test_connection_not_recovered(self):
        self.assertEqual(evaluate([job(connection_health="unhealthy")])["suggested_count"], 0)

    def test_replay_not_safe(self):
        self.assertEqual(evaluate([job(replay_safe=False)])["suggested_count"], 0)

    def test_not_approved(self):
        self.assertEqual(evaluate([job(approved=False)])["suggested_count"], 0)

    def test_duplicate_in_input(self):
        result = evaluate([job(), job()])
        self.assertEqual(result["suggested_count"], 1)
        self.assertEqual(result["rejected_count"], 1)

    def test_previously_replayed(self):
        self.assertEqual(evaluate([job()], {"job-1"})["suggested_count"], 0)

    def test_batch_size(self):
        result = evaluate([job(job_id=f"job-{i}") for i in range(60)])
        self.assertEqual([len(b["job_ids"]) for b in result["suggested_batches"]], [25, 25, 10])
        self.assertTrue(all(len(b["job_ids"]) <= MAX_BATCH_SIZE for b in result["suggested_batches"]))

    def test_successful_job(self):
        self.assertEqual(evaluate([job(status="succeeded")])["suggested_count"], 0)

    def test_missing_ids(self):
        self.assertEqual(evaluate([job(job_id=None)])["rejected_count"], 1)


if __name__ == "__main__":
    unittest.main()
