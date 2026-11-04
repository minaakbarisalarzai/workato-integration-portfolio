# Offline and future live verification

## Offline automated tests

Run `python3 -m unittest discover -s tests -v`. Covered examples:

1. Healthy, approved, replay-safe failure eligible for dry-run grouping.
2. Non-connection error refused.
3. Connection not restored refused.
4. Replay-unsafe job refused.
5. Job without approval refused.
6. Duplicate job ID suppressed.
7. Previously replayed job suppressed.
8. Batches never exceed 25 job IDs.
9. Successful job refused.

## Workato sandbox checks (not completed by these files)

- Inspect the actual recipe and its connection filters.
- Confirm precise failed-job type/category mapping, not merely `status == failed`.
- Verify connection health using an authorized sandbox mechanism.
- Verify time-window boundaries and pagination.
- Test simultaneous failures, rate limits, long-running reruns and partial success.
- Validate permissions, deduplication across scheduled executions, and audit behavior.
- Exercise a replay-safe idempotent test integration; never use financial/customer mutations as a first test.
- Compare intended and observed reruns, including follow-up job statuses.
