# Case Study 01 — Consolidating HTTP Actions into Python

**Goal:** Compare a Workato recipe with five HTTP connector actions and per-action monitoring to a recipe containing one Python action that executes the same five read-only REST operations.

## Public API operations

| Logical call | GET endpoint |
|---|---|
| User | `/users/1` |
| Posts | `/posts?userId=1` |
| Comments | `/posts/1/comments` |
| Todos | `/users/1/todos` |
| Albums | `/users/1/albums` |

Base URL: `https://jsonplaceholder.typicode.com`.

## Baseline design

`Scheduler → Monitor(GET user → IF name → log) → Monitor(GET posts) → Monitor(GET comments) → Monitor(GET todos) → Monitor(GET albums)`. The screenshots also show retry/no-retry branches and job-report logging. Some of those actions execute **only when the corresponding branch runs**, so do not equate total steps shown with tasks billed. The observed job consumed **five tasks**.

## Optimized design

`Scheduler → Python: Fetch and Validate Related API Resources`. The Python code in [`optimized.py`](optimized.py) makes five sequential GET requests, checks response type, validates the user ID, retries selected transient HTTP failures and returns structured results. The observed successful job consumed **one task**.

### Input example

```json
{"user_id":1,"post_id":1,"expected_name":"Leanne Graham"}
```

### Output fields

`success` (boolean), `name_matches` (boolean), `user_name` (string), `posts_count`, `comments_count`, `todos_count`, `albums_count`, `completed_operations`, `error_count` (integers), `error_message` (string), `summary` (object), `http_attempts_on_success` (nullable integer).

## Error-handling policy

- Input validation rejects non-positive/non-integer user or post IDs.
- Each request has an 8-second timeout and at most two attempts for timeouts, connection errors, or HTTP 429/500/502/503/504.
- Non-retryable HTTP errors and malformed JSON stop the sequence.
- No raw API response bodies, tokens, or personal information are logged.
- **Important:** `success=false` is a structured *business output*, not a raised Workato error. If you require job failure or monitoring alerts, configure a Workato IF on `success` and an explicit escalation/fail action. The minimal optimized screenshot only contains one Python action, so do not claim the full baseline monitoring policy is reproduced by the recipe itself.
- Success-path `http_attempts_on_success` is supplied to distinguish API attempts from Workato tasks; on failure this is null because attempts are not fully tracked on exceptional exits.

## Observed sample

| | Baseline | Optimized |
|---|---:|---:|
| Job | Successful | Successful |
| Tasks used | 5 | 1 |
| Duration | 910 ms | 897 ms |

**80% fewer observed Workato tasks for these executions.** No claim is made about guaranteed bill savings, reduced API traffic, or overall production resiliency. Endpoint-by-endpoint equivalence remains to be independently verified.

## Files

- [`optimized.py`](optimized.py) — complete Workato Python snippet
- [`screenshots/`](screenshots/) — Workato recipe and live job screenshots

## Screenshot evidence

**Baseline — five HTTP requests with Workato error-handling branches:**

![Baseline beginning](screenshots/01-http-baseline-top.png)
![Baseline middle](screenshots/02-http-baseline-middle.png)
![Baseline lower middle](screenshots/03-http-baseline-lower-middle.png)
![Baseline final portion](screenshots/04-http-baseline-bottom.png)

**Optimized — single Python action:**

![Optimized Python recipe](screenshots/05-python-optimized.png)

**Measured successful Workato job results:**

![Baseline: five tasks, 910 ms](screenshots/06-http-job-result.png)
![Optimized: one task, 897 ms](screenshots/07-python-job-result.png)

- [`../docs/BENCHMARKS.md`](../docs/BENCHMARKS.md) — benchmark interpretation
