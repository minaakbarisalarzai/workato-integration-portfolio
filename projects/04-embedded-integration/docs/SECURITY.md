# Security review and publication checklist

## Source provenance and explicit caution

The original capstone archive included real-looking hardcoded access tokens, RSA private signing key material, cloud resource identifiers, and API endpoints. **Those values are deliberately omitted from this reconstructed sample.** Any potentially active key/token must be revoked or rotated by its authorized owner. Deleting a leaked key from Git does not remove it from Git history or backups.

## Improvements in the portfolio sample

- No private keys, bearer tokens, tenant identifiers, AWS account IDs, or customer data are bundled.
- Server-side tenant identity is bound to verified authorizer context; browser-supplied `customerId` is ignored.
- Workato JWTs have 60–900 second bounded lifetimes; the default is 300 seconds.
- Origin is configured, not inferred from a caller-controlled request.
- `postMessage` checks **exact** origin and iframe source (not substring matching).
- Frame navigation is restricted to an explicit list of paths.
- Failed upstream responses are summarized with safe codes rather than logging body/token.
- Provisioning webhooks are rejected unless trusted authorizer context confirms verification.
- Package copying and collaborator invitation delivery are not falsely presented as live-tested capabilities.

## Deployment blockers (must resolve before live rollout)

1. Establish **written permission** to release employer-linked intellectual property, source, screenshots, and video; replace non-public materials with original diagrams/examples where needed.
2. Revoke or rotate any exposed Workato API token or RSA private key and inspect other services for their use. Do not paste these values into tickets/chats/docs.
3. Implement real host authentication + tenant-based authorization, gateway authorizer, and session/CSRF controls. The demo provides only the **handler side** of that boundary.
4. Implement authenticated webhook signature verification plus freshness/replay protection **outside or before** the provisioning handler.
5. Configure strict CSP as HTTP response headers in the host (meta CSP in demo is defense-in-depth, not equivalent); set appropriate `frame-ancestors`, `Referrer-Policy`, HSTS, and cache restrictions.
6. Use AWS Secrets Manager / KMS / scoped IAM; never put secrets in bundled JS, Git history, environment screenshots, or browser logs.
7. Validate current Workato supported embed and managed-user API operations and JWT claims against your assigned tenant.
8. Add provisioning idempotency, state transitions, concurrency handling, monitoring, alerting, and chaos/failure tests before production.
9. Define JWT revocation strategy and avoid logging full iframe URLs containing tokens.

## Public repository scan

Before publishing: run a suitable secrets scanner (e.g. `gitleaks detect` or GitHub secret scanning), review binary files, inspect screenshots and diffs, and verify `.gitignore`. If secrets were committed, rotate them first and address history using approved processes.
