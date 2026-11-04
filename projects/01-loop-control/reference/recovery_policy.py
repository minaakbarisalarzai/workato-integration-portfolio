"""Conservative *dry-run* eligibility evaluator for synthetic Workato-like jobs.

This standalone educational example NEVER contacts Workato or retries jobs.
It is not an export or reconstruction of an employer's production recipe.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

ALLOWED_FAILURES = frozenset({"connection_unavailable", "connection_timeout"})
MAX_BATCH_SIZE = 25


def evaluate(jobs: list[dict], previously_replayed: set[str] | None = None) -> dict:
    """Return suggested batches and auditable rejection reasons, without side effects."""
    replayed = set(previously_replayed or ())
    seen: set[str] = set()
    eligible: dict[str, list[str]] = {}
    decisions: list[dict] = []

    for record in jobs:
        job_id = record.get("job_id")
        recipe_id = record.get("recipe_id")
        reason = None
        if not isinstance(job_id, str) or not job_id.strip() or not isinstance(recipe_id, str) or not recipe_id.strip():
            reason = "missing_job_or_recipe_id"
        elif job_id in seen:
            reason = "duplicate_in_input"
        elif job_id in replayed:
            reason = "already_replayed"
        elif record.get("status") != "failed":
            reason = "not_failed"
        elif record.get("error_category") not in ALLOWED_FAILURES:
            reason = "not_eligible_failure_category"
        elif record.get("connection_health") != "healthy":
            reason = "connection_not_confirmed_healthy"
        elif record.get("replay_safe") is not True:
            reason = "replay_safety_not_confirmed"
        elif record.get("approved") is not True:
            reason = "approval_required"
        if isinstance(job_id, str):
            seen.add(job_id)
        if reason:
            decisions.append({"job_id": job_id, "recipe_id": recipe_id, "decision": "reject", "reason": reason})
        else:
            decisions.append({"job_id": job_id, "recipe_id": recipe_id, "decision": "suggest", "reason": "dry_run_only"})
            eligible.setdefault(recipe_id, []).append(job_id)

    batches = [
        {"recipe_id": recipe_id, "job_ids": ids[start : start + MAX_BATCH_SIZE], "dry_run": True}
        for recipe_id, ids in eligible.items()
        for start in range(0, len(ids), MAX_BATCH_SIZE)
    ]
    return {"suggested_batches": batches, "decisions": decisions,
            "suggested_count": sum(len(b["job_ids"]) for b in batches),
            "rejected_count": sum(d["decision"] == "reject" for d in decisions)}


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 -m reference.recovery_policy examples/synthetic_jobs.json")
    records = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(evaluate(records["jobs"]), indent=2))


if __name__ == "__main__":
    main()
