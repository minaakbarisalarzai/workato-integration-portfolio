# Code review notes and suggested production backlog

## Original architecture: strengths

- End-to-end understanding of Workato embedding, APIs, webhooks, and serverless integration.
- Strong demonstration of component orchestration and support for multiple tenants.
- Clear applied use of iframe navigation, JWT, provisioning, folder trees, and asynchronous invitation queueing.

## Original source: changes required before publication

- Embedded private key and Workato tokens were found in uploaded source; excluded from this repo.
- Client-supplied customer ID could select another tenant; this sample uses verified authorizer context.
- PostMessage origin substring matching allowed a spoofed subdomain; corrected.
- Folder lookups keyed only by name could cross-map Sandbox and Production; corrected.
- Single large Lambda mixed provisioning, package transfer and invitations; separated.
- Original code assumed cloud responses and printed upstream HTTP bodies; safer errors used.
- Imported packages were not guaranteed atomic or idempotent; copy service intentionally gated.

## Next engineering improvements

1. Add Terraform/CDK with configurable authorizer, IAM roles, secrets policy, SQS DLQ, and alarms.
2. Introduce an idempotency store keyed by signed webhook event ID and use Step Functions for state tracking.
3. Confirm current Workato endpoints, rate limits and exact API schemas in a sandbox.
4. Add an invitation worker with tenant-validated collaborator mapping and proper role scopes.
5. Add integration tests against a dedicated test tenant, including malformed upstream JSON, 409, 429, 5xx, and request timeouts.
6. Document compatibility with modern browser third-party cookie and iframe restrictions.
7. Add a live screenshot/demo **only after** permission and credential/privacy review.
