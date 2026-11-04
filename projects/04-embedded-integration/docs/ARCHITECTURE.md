# Architecture and Boundaries

## Embedded navigation (trusted path)

1. The host application authenticates the user and authorizes exactly one tenant.
2. An API Gateway authorizer derives a verified principal ID and authorized tenant ID; untrusted query strings cannot set either field.
3. The frontend requests `POST /api/embed/session` using same-origin credentials.
4. The broker queries Workato for the managed-user team ID, creates an RS256 JWT (`sub`, `iat`, `exp`, `jti`, `origin`), and returns it with `Cache-Control: no-store`.
5. The frontend builds an allowlisted Workato direct-link URL and updates the iframe.
6. The frame only accepts display-related messages from the exact Workato origin and active iframe window.

## Provisioning (trusted path)

1. An authorized host tenant event arrives at API Gateway.
2. Gateway authenticates the event sender and validates replay resistance before attaching `webhookAuthorized=true`.
3. Python Lambda checks the trusted authorizer result and validates event fields.
4. Workato managed-user API creates a managed account; folder discovery/creation initializes Sandbox and Production trees.
5. Optional collaborator messages are queued to SQS for a separately authenticated invitation worker. **This reference intentionally does not implement sending actual invitation emails**.
6. Optional template copying is intentionally disabled pending current Workato API contract and permissions review.

## Design decisions

- AWS API Gateway and Lambda are logical infrastructure components; no deployed AWS stack is packaged.
- No cross-tenant ID is accepted from browser parameters.
- Token key material remains only on the server and should be backed by Secrets Manager/KMS.
- Endpoint and authentication details must be checked against current Workato Embedded documentation.
- Folder initialization uses `(parent_id, name)` keys rather than flat names (correcting a source-design ambiguity).
- Provisioning is a multi-step external side-effect workflow, not transactional. Add idempotency keys, deduplication, compensating actions, and execution state before production deployment.
- The Workato API can have schema variants. This reference models the historical managed-user/folder contract and makes no guarantees for a current tenant.

## Threat boundaries to test

| Boundary | Required control |
|---|---|
| Browser → session API | Host login, CSRF protections, gateway authorizer, tenant binding |
| Session Lambda → Workato | Scoped token, TLS, timeouts, no response-body logging |
| Embed JWT → iframe | Short TTL, RS256 signature, validated origin, strict no-store |
| Host webhook → provisioning | Authenticated and replay-resistant webhook at edge |
| Provisioning → Workato | API least privilege, idempotent provisioning design |
| Provisioning → SQS | Encryption, queue policy, scoped IAM and worker authorization |
