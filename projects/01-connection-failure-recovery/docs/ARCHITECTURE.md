# Architecture and observed workflow

## Observed Workato recipe

```text
Schedule (every five minutes)
  -> Search recipes
  -> For each recipe
       -> List connections
       -> If any connections returned
            -> Search jobs in a bounded time range
            -> For each job
                 -> If status == failed
                      -> Monitor
                           -> Rerun specified jobs (Batch)
                           -> Append a Google Sheets log
                      -> On error: Do Not Retry; append failure log
                 -> Else: log to job report
```

The diagram summarizes visible steps; it is not an executable Workato recipe export. The `connections.length > 0` conditional tests *presence*, not connection *failure*. The schedule alone is not proof of how history windows, errors, or pagination are configured.

## Recommended safer target architecture (not shown as implemented)

```text
Workato failure events or bounded job-history poll
  -> classify root cause
  -> check associated connection recovery
  -> check allowlist / replay safety / duplicate replay state
  -> approve eligible batch (max 25)
  -> invoke Workato rerun API/action
  -> verify rerun outcomes
  -> write durable audit record / escalate unsafe cases
```

A job's failed status is not sufficient evidence for retry. A connection returning to a healthy state does not guarantee that replay is idempotent. Favor a documented review process for workflows that may charge customers, mutate records, or send communications.
