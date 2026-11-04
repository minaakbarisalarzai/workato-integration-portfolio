# Workato Connection Failure Detection & Automated Job Recovery

**Integration reliability · Workato RecipeOps / platform automation · Failed-job triage · Controlled recovery**

**Portfolio author:** Mina Akbari  
**Type:** Workato workflow case study with an independently authored recovery-policy reference implementation  
**Status:** Workflow illustrated by screenshots; reference policy tested locally. **Live recovery, connection-health enforcement, and API behavior have not been verified from these materials.**

## The problem

A transient connection outage can cause a group of integration jobs to fail. Manually finding affected recipes, inspecting job histories, and replaying eligible jobs is tedious and error-prone. This workflow explores the operational automation needed to identify failed executions, initiate batch reruns, and log outcomes.

## Original Workato workflow (one continuous recipe)

The three images below are **consecutive portions of the same recipe**, not separate workflows. The visible steps show:

1. Run on a five-minute schedule.
2. Search recipes in the workspace and iterate over the results.
3. List connections and check whether the returned collection is nonempty.
4. Search job history for a recipe within a chosen time window.
5. Iterate over jobs and check `status == failed`.
6. Invoke **Rerun specified jobs** inside a Monitor block.
7. Record a rerun or error-path outcome in Google Sheets, with a Do Not Retry branch and a fallback log.

**Critical limitation:** A nonempty connection list is *not* evidence that a connection was down or restored; `status == failed` also does not establish the root cause. The screenshots do not establish deduplication, retry safety, or connection-health verification. Do not use the depicted flow to automatically replay arbitrary production failures without those safeguards.

### Full recipe — section 1/3
![Workflow overview](screenshots/01-workflow-overview.png)

### Full recipe — section 2/3
![Workflow continuation](screenshots/02-workflow-continuation.png)

### Full recipe — section 3/3
![Workflow completion](screenshots/03-workflow-completion.png)

## Portfolio reference implementation

The [`reference/`](reference/) package is **new, independently written sample code**, not an export or transcription of the Workato recipe. It demonstrates a conservative, **dry-run-only** policy for evaluating synthetic failed jobs. It does not call Workato, modify recipes, or trigger reruns.

It illustrates:

- explicit classification of connection-related errors;
- connection-health gates;
- replay-safe workload allowlists and manual approval gates;
- duplicate-job suppression;
- bounded groups (25 job IDs maximum per suggested batch);
- a structured, auditable decision summary.

For production use, additional review is needed for durable replay history, connection-to-recipe mapping, API pagination, execution windows, concurrency, service-side idempotency, and verification that the original operation cannot duplicate side effects. A failed job may have succeeded at some earlier steps, and rerunning it may execute the latest recipe revision.

### Run the offline example

```bash
python3 -m reference.recovery_policy examples/synthetic_jobs.json
python3 -m unittest discover -s tests -v
```

**No external packages or credentials required.**

## Project contents

```text
01-connection-failure-recovery/
├── README.md
├── .gitignore
├── LICENSE
├── screenshots/                 # Three views of one Workato recipe
├── docs/
│   ├── ARCHITECTURE.md
│   ├── RECOVERY_POLICY.md
│   ├── TEST_PLAN.md
│   └── PUBLICATION_CHECKLIST.md
├── examples/
│   └── synthetic_jobs.json
├── reference/
│   ├── __init__.py
│   └── recovery_policy.py       # Dry-run policy evaluator, no API calls
└── tests/
    └── test_recovery_policy.py
```

## What this demonstrates for an integration engineering role

Beyond connecting applications, the workflow focuses on *operating* integrations: discovery, execution history, control flow, error monitoring, batch action invocation, and audit logging. The reference policy adds defensive design and testable recovery eligibility decisions.

## Security, provenance, and permissions

The screenshot images were supplied from an existing Workato recipe. They may originate from a corporate environment. **Review publication authorization before posting screenshots or workflow details publicly** and crop/redact identifiers as necessary. Do not upload a company recipe export, connection secrets, customer records, internal URLs, or proprietary configurations without written permission. Synthetic example data and the independent Python reference code are designed for public demonstration. See [publication checklist](docs/PUBLICATION_CHECKLIST.md).

## Next steps

- Validate a failure taxonomy using synthetic connection-failure scenarios.
- Verify Workato API/action parameters and account-specific permissions in an authorized sandbox.
- Integrate a connection-health verification mechanism before recovery.
- Add durable replay state, manual review, and audit trails before enabling any actual rerun action.
- Run Workato test jobs and document observed results separately from offline policy tests.

**Demonstration only. Not a production-safe automatic recovery system.**
