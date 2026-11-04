
# Case Study 01 — Consolidating HTTP Actions into Python

**Author:** Mina Akbari  
**Platform:** Workato  
**Technologies:** Python, HTTP, REST APIs, JSON  
**Focus:** Task Efficiency · Cost Optimization · Workflow Simplification

## Overview

This case study demonstrates how consolidating multiple HTTP connector actions into Python can significantly reduce Workato task consumption and simplify an integration workflow.

The original recipe used five separate HTTP requests, along with conditional logic, monitoring, error handling, and logging.

The optimized recipe performs the same five external REST API operations through a consolidated Python implementation.

### Key Results

- **88.2% fewer Workato tasks:** 17 → 2 per successful execution.
- **91.3% fewer configured workflow actions:** 23 → 2.
- **15 Workato tasks eliminated per execution.**
- Both compared jobs completed successfully.

## The Problem

The baseline Workato recipe retrieves related information from five REST API endpoints.

Although the integration works, its multiple HTTP connector actions and supporting monitoring and logging logic increase the number of steps required to maintain and execute the workflow.

The original implementation contained **23 configured workflow actions** and consumed **17 Workato tasks** during the observed successful execution.

This matters because unnecessary task consumption can increase usage-based costs in task-metered Workato environments, particularly for recipes that execute frequently.

## Public API Operations

The example uses the public read-only [JSONPlaceholder API](https://jsonplaceholder.typicode.com/).

| Logical Call | GET Endpoint |
|---|---|
| User | `/users/1` |
| Posts | `/posts?userId=1` |
| Comments | `/posts/1/comments` |
| Todos | `/users/1/todos` |
| Albums | `/users/1/albums` |

Both implementations execute the same five logical API requests.

The optimization reduces Workato actions and task consumption, not the number of external API operations.

## Baseline Design — Multi-step HTTP Workflow

The original recipe uses individual HTTP connector actions to perform each API request, with additional monitoring, conditional processing, and logging.

### Workflow

```text
Scheduler
    |
    v
HTTP GET User
    |
    v
Validate User Name
    |
    v
HTTP GET Posts
    |
    v
HTTP GET Comments
    |
    v
HTTP GET Todos
    |
    v
HTTP GET Albums
    |
    v
Monitoring, Error Handling & Logging
```

The actual recipe includes Monitor blocks, retry/no-retry branches, and supporting logging actions.

**Baseline measurements:**

- 23 configured workflow actions.
- 17 Workato tasks consumed in the observed successful job.
- 910 ms observed execution duration.

Not every configured action runs during every execution. Conditional and error-handling branches may execute only when their conditions are met.

## Optimized Design — Consolidated Python

I redesigned the integration to consolidate the five API calls and their supporting request-handling logic into Python.

### Workflow

```text
Scheduler
    |
    v
Python: Fetch and Validate Related API Resources
    |
    v
Structured Output
```

The optimized implementation uses [optimized.py](optimized.py) to:

1. Validate the provided user and post IDs.
2. Execute five sequential REST API requests.
3. Check HTTP response status codes.
4. Retry selected transient failures.
5. Parse and validate JSON responses.
6. Verify the expected user information.
7. Collect the returned resource counts.
8. Return a structured result containing operation status and error information.

**Optimized measurements:**

- 2 configured workflow actions.
- 2 Workato tasks consumed in the observed successful job.
- 897 ms observed execution duration.

### Example Input

```json
{
  "user_id": 1,
  "post_id": 1,
  "expected_name": "Leanne Graham"
}
```

### Output Fields

The Python implementation returns structured fields including:

- `success`
- `name_matches`
- `user_name`
- `posts_count`
- `comments_count`
- `todos_count`
- `albums_count`
- `completed_operations`
- `error_count`
- `error_message`
- `summary`
- `http_attempts_on_success`

## Results — November 4, 2026

Both the baseline and optimized recipes completed successfully.

| Measurement | Multi-step HTTP | Consolidated Python |
|---|---:|---:|
| Job status | Successful | Successful |
| Configured workflow actions | **23** | **2** |
| Workflow actions eliminated | — | **21** |
| Workflow action reduction | — | **91.3%** |
| Workato tasks consumed | **17** | **2** |
| Workato tasks eliminated | — | **15** |
| Task consumption reduction | — | **88.2%** |
| Job duration | **910 ms** | **897 ms** |

### Result 1 — 88.2% Reduction in Task Consumption

The optimized recipe reduced Workato task usage from 17 tasks to 2 tasks per observed successful execution.

This represents **15 fewer Workato tasks per execution**.

For Workato environments with task-based billing, this reduction improves resource efficiency and can lower usage-based costs.

### Result 2 — 91.3% Simpler Workflow

The original workflow contained 23 configured actions.

The optimized design contains 2.

By eliminating 21 actions, the recipe becomes easier to navigate and reduces repetitive configuration.

### Result 3 — Successful API Processing

The optimized execution produced the following results:

| Validation | Observed Result |
|---|---|
| `success` | `true` |
| `name_matches` | `true` |
| `completed_operations` | `5` |
| `error_count` | `0` |
| Posts | 10 |
| Comments | 5 |
| Todos | 20 |
| Albums | 10 |

The optimized workflow completed all five intended API operations successfully.

The baseline was also successful. A detailed endpoint-by-endpoint comparison of all response fields has not been separately documented.

## Business Impact — Cost Efficiency at Scale

Reducing task consumption becomes increasingly valuable as integration volume grows.

Assuming the observed task counts remain consistent:

| Monthly Executions | Original Tasks | Optimized Tasks | Tasks Saved |
|---|---:|---:|---:|
| 1,000 | 17,000 | 2,000 | **15,000** |
| 10,000 | 170,000 | 20,000 | **150,000** |
| 100,000 | 1,700,000 | 200,000 | **1,500,000** |

At 10,000 executions per month, this design would consume **150,000 fewer Workato tasks** than the original implementation.

These are projected task savings based on the observed executions. Actual monetary savings depend on the applicable Workato contract and billing model.

## Error Handling

The consolidated Python implementation includes request validation and HTTP error handling.

### Implemented Behavior

- Rejects invalid, non-positive user or post IDs.
- Uses an 8-second timeout per request attempt.
- Allows up to two attempts for selected transient errors.
- Handles connection failures and timeouts.
- Retries HTTP 429, 500, 502, 503, and 504 responses within the configured limit.
- Stops execution of the request sequence on non-retryable errors or malformed JSON.
- Returns structured error information.
- Avoids logging raw API response bodies or credentials.

### Workato Error Propagation

The Python implementation can return `success=false` when an API operation fails.

However, returning a structured error does not automatically mark the Workato job as failed.

For production use, the recipe should evaluate the Python result and explicitly raise or escalate failures where appropriate.

The consolidated design also moves much of the step-level observability into Python, so logging and error reporting require careful consideration.

## Design Tradeoffs

| Consideration | Multi-step HTTP | Consolidated Python |
|---|---|---|
| Workato task consumption | Higher | Lower |
| Recipe action count | 23 | 2 |
| API requests | 5 | 5 |
| Request handling | Distributed | Centralized |
| Error handling | Workato Monitor branches | Python handling and structured results |
| Troubleshooting | Individual Workato actions | Python logs and structured output |
| Maintenance | Visual configuration | Python code maintenance |

The optimal approach depends on integration complexity, observability requirements, and maintainability.

Python consolidation is particularly useful when repeated API operations and supporting logic create unnecessary Workato tasks.

## Screenshot Evidence

### Baseline — Five HTTP Requests with Monitoring and Logging

**Section 1 — Beginning of the original workflow**

![Baseline beginning](screenshots/01-http-baseline-top.png)

**Section 2 — Additional HTTP actions and monitoring**

![Baseline middle](screenshots/02-http-baseline-middle.png)

**Section 3 — Conditional processing and error handling**

![Baseline lower middle](screenshots/03-http-baseline-lower-middle.png)

**Section 4 — Remaining actions and logging**

![Baseline final portion](screenshots/04-http-baseline-bottom.png)

### Optimized — Consolidated Python Workflow

The optimized design replaces the repeated API actions and supporting logic with a streamlined Python-based implementation.

![Optimized Python recipe](screenshots/05-python-optimized.png)

### Workato Job Execution Results

**Original — 17 tasks, 910 ms**

![Baseline successful job — 17 tasks](screenshots/06-http-job-result.png)

**Optimized — 2 tasks, 897 ms**

![Optimized successful job — 2 tasks](screenshots/07-python-job-result.png)

The duration measurements come from one successful execution of each design. The 13 ms difference should not be interpreted as a statistically significant performance improvement.

## Project Files

- [optimized.py](optimized.py) — Consolidated Python implementation.
- [screenshots/](screenshots/) — Before-and-after recipe screenshots and Workato job results.
- [Benchmarks](../docs/BENCHMARKS.md) — Measurement details and benchmark interpretation.

## Key Takeaway

**Reduced Workato task consumption by 88.2% and configured workflow actions by 91.3%, while successfully completing the same five external REST API operations.**

This case study demonstrates how consolidating repetitive integration logic can improve platform resource efficiency, simplify recipe design, and reduce task-metered usage costs.

---

**Developed and documented by Mina Akbari.**
