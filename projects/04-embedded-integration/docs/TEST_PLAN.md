# Verification Plan

## Reproducible offline checks

```bash
node --test services/embed-session/test/*.test.mjs web/*.test.mjs
PYTHONPATH=services/provisioning python3 -m unittest discover -s services/provisioning/tests -v
python3 -m compileall -q services/provisioning
```

These offline tests cover the authorizer boundary, JWT structure/signature, tenant ID validation, upstream error classification, allowlisted routes, exact-origin message checks, payload validation, folder parent scoping, queue handoff, and disabled template copying.

## Manual/live test matrix (NOT performed for this sanitized reference)

| Scenario | Expected | Status |
|---|---|---|
| Verified logged-in host user | JWT only for authorized tenant | Not run |
| Attempt cross-tenant embed access | Blocked at authorizer | Not run |
| Missing/invalid webhook signature | Rejected | Not run |
| Workato API rate limit | Bounded safe error | Not run |
| JWT origin mismatch / expired session | Workato rejects session | Not run |
| Tenant provisioning duplicate event | Exactly-once effective behavior | Not implemented |
| Concurrent folder provisioning | No duplicate folders | Not implemented |
| Collaborator invitations worker | Authorized role mapping and delivery | Not implemented |
| Template export/import | Correct package and target | Not implemented |
| Full browser embedding | Functional UX in authorized tenant | Not run |

**No production/readiness claim should be made from the offline test suite alone.**
