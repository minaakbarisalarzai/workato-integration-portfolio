# Benchmark methodology and observed evidence

## Case Study 01 — Workato job observations

Observed from user-provided Workato job screenshots dated November 4, 2026:

| Metric | Baseline HTTP | Consolidated Python |
|---|---:|---:|
| Status | Successful | Successful |
| Workato tasks used | 5 | 1 |
| Duration (ms) | 910 | 897 |

Calculation: `(5 - 1) / 5 * 100 = 80%` task reduction in the observed runs.

A single sample is **not** proof of a faster workflow overall. The 13 ms difference may be ordinary measurement noise. No actual cost saving is computed because licensing terms are unknown. Consolidation does not decrease the five intended external GET requests. Baseline job shows a true condition; optimized job shows `completed_operations=5`, `success=true` and counts. Detailed raw-response equivalence was not provided.

## Case Study 02 — Workato code and output observations

- Baseline recipe: two Python actions (encoder and decoder).
- Optimized recipe: one Python decoder action using a Workato formula on the input.
- Screenshots show matching Base64 strings for the same sample input.
- Output equivalence of the final decoder and actual tasks/job for these recipes are not yet documented.

## Recommended future measurement protocol

1. Use the same payload, user IDs, API endpoints, and recipe versions.
2. For the API case, capture all five HTTP response statuses and normalized outputs in both implementations.
3. Run each recipe at least 10 times under similar conditions; save raw durations and tasks per job.
4. Calculate medians and a range; keep monitoring/error handling differences explicit.
5. Capture positive and negative test cases, including rate limiting, 404, malformed data, and retry behavior.
6. For the Base64 case, compare decoded JSON data, then note whether byte-for-byte Base64 matches.
7. Never use actual customer data or employer-owned integrations for a public benchmark.
