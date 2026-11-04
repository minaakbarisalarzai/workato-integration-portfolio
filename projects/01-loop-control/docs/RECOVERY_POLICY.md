# Recovery policy — portfolio reference

The accompanying Python module evaluates **synthetic jobs** and emits **suggested dry-run batches** only. No Workato API requests are made.

## Eligibility requirements

- Status equals `failed`.
- Error category is explicitly `connection_unavailable` or `connection_timeout`.
- Corresponding connection health is `healthy` (confirmed externally in the scenario data).
- Recipe is marked `replay_safe` in the sample record.
- Job has `approved: true` (manual approval is an explicit gate).
- Job ID has not been replayed previously and is unique in this evaluation.

Rejected records include an audit reason. No assumption is made about connection-to-recipe mapping outside the supplied synthetic records. For real systems, that mapping, privilege boundaries, and health evidence must be verified against authoritative APIs.

## Batch limits and replay safety

Suggested groups contain no more than **25 job IDs**. This limit is a conservative reference value for Workato's documented bulk rerun behavior; confirm the limits of the exact API/action used before deployment. A failed job can have completed some earlier steps. Replaying a job may create duplicate side effects or run a newer recipe version. A replay-safe flag is illustrative and **not itself sufficient** for production approval.

## Audit expectations

Every decision should have job ID, recipe ID, error category, outcome, reason, and audit timestamp in a real implementation. A production solution should persist replay keys and outcomes in a transactional store, rather than relying on an in-memory set or an appended spreadsheet alone.

## Non-goals

- No Workato credentials or infrastructure access.
- No detection of actual connection outages.
- No API integration or automatic rerun.
- No claims of successful production recovery.
