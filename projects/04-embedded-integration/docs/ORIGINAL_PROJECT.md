# Original Project — Source, Scope and Differences

**Academic work:** *Embedded Innovation Studio*, Mina Akbari, master's project, report dated January 5, 2025.

**Public demonstration:** https://www.youtube.com/watch?v=VWJzLgZdENw

The author-supplied report describes:

- An HTML iframe providing embedded Workato/Innovation Studio UI and an RS256 JWT.
- A customer-created webhook from LoanPro to API Gateway and AWS Lambda.
- Workato managed-customer provisioning.
- Collaborator invitation and role assignment.
- LoanPro custom Workato connector and API search actions.
- Workspace folders under Sandbox/Production, with a subsequent plan for solution sets.
- Resource thresholds/quotas as **future work**, not delivered functionality.

The uploaded Python Lambda added template export/import and SQS enqueue logic, but the report's completion claims and code should not be confused with independent production acceptance testing.

## What this repository deliberately changes

- Uses a **generic host app** and fictional example data, not LoanPro-specific application code.
- Removes original secrets, hardcoded cloud IDs, legacy implementation files, vendor endpoints beyond generic documented routes, and copies of dependencies.
- Replaces client-provided tenant selection with trusted gateway authorizer context.
- Separates front-end, session brokerage, provisioning, HTTP client, and optional service adapters.
- Replaces broad iframe origin substring checks with strict origin+source checks.
- Models old API contracts as unverified until retested in an authorized tenant.
- Keeps template-copy API implementation **disabled** rather than publishing an unverified operation that could mutate customer workspaces.

**Honesty statement:** This is a new security-oriented portfolio/reference refactor inspired by the master's capstone, not a drop-in replacement or a claim the refactored code ran in the original environment.
