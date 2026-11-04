# Workato Connection Failure Detection & Automated Job Recovery

**Author:** Mina Akbari  
**Platform:** Workato  
**Focus:** Internal integration operations, failed-job investigation, batch replay, and recovery logging

## Why this matters

When an external connection is temporarily unavailable, multiple integration jobs can fail. Locating affected recipes, reviewing their job histories, and initiating reruns individually takes time and increases operational effort. This Workato recipe brings those activities into one operational workflow.

## The process

1. **Run every five minutes.** Start a scheduled inspection.
2. **Discover recipes.** Search for recipes in the workspace and iterate over the results.
3. **Look up connections.** Search connections for each recipe using a configured connector filter. The source example uses a MySQL filter; it is not a universal connection-outage detector.
4. **Inspect execution history.** Request jobs for the recipe in a configured time window, filtered for failed status.
5. **Evaluate failed jobs.** Follow the failed-job condition and invoke Workato's **Rerun specified jobs** action.
6. **Record results.** Use Google Sheets to record recovery-action outcomes, with a Monitor branch, Do Not Retry handling, and fallback logging.

## Result and value

The configured recipe demonstrates how Workato can automate **operational tasks within Workato itself**, not just integrations between external systems. It consolidates recipe discovery, connection lookup, failed-job inspection, rerun initiation, and logging into one workflow. This can reduce manual navigation and provide a more consistent response to a disruption.

**Verification scope:** The screenshots and sanitized recipe export establish the workflow configuration. They do not independently demonstrate successful recovery across a real outage, quantified time savings, or that every selected failure was connection-related. No such numbers are claimed.

## Recipe walkthrough (one continuous recipe)

These three screenshots are consecutive views of **the same Workato recipe**.

### Section 1 — Recipe discovery and connection lookup

![Recipe overview](screenshots/01-workflow-overview.png)

### Section 2 — Failed-job processing and rerun action

![Recipe continuation](screenshots/02-workflow-continuation.png)

### Section 3 — Error handling and logging

![Recipe completion](screenshots/03-workflow-completion.png)

## Recipe definition

[`recipe/recipe_export_SANITIZED_REFERENCE.json`](recipe/recipe_export_SANITIZED_REFERENCE.json) is a **redacted reference copy** of the original Workato recipe definition, not an import-ready deployment artifact. Connection assignments, spreadsheet identifiers, and fixed search dates have been replaced with demonstration values. 

## Operational safeguards and limitations

- A matching connection and `failed` status do **not** establish that a job failed because of a connection outage.
- Recovery should verify connection health and classify the failure before replaying it.
- Rerunning a job may duplicate side effects from earlier successful steps. Use approval or idempotency controls where necessary.
- Set an accurate outage window and enforce per-recipe batch limits before executing reruns.
- Preserve an audit trail that differentiates a rerun request from successful completion of the rerun job.

The example export is included for **technical review**, not unattended production execution.

## Project files

```text
01-connection-failure-recovery/
├── README.md
├── recipe/
│   └── recipe_export_SANITIZED_REFERENCE.json
└── screenshots/
    ├── 01-workflow-overview.png
    ├── 02-workflow-continuation.png
    └── 03-workflow-completion.png
```
