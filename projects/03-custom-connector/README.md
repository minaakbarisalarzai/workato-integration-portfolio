# GitHub Issue Explorer — Workato Custom Connector

**One read-only action. Professional connector engineering with Workato SDK (Ruby).**

> **Verification status:** Ruby syntax checked; **19 offline tests / 59 assertions passing**. The previous connector version was tested live in Workato: token connection, issue listing (3 issues), start/end pagination, label filtering, and `per_page=101` validation. **This improved version has not yet been retested in Workato**. Do not present it as production-deployed.

## What it does

The connector adds a **List repository issues** action in Workato. A recipe author selects an owner, repository, issue state, sorting, and optionally a label, then retrieves a page of issues from GitHub. The output includes simplified issue objects, count, and `next_page`/`has_more` pagination metadata.

**Demo workflow:** `Scheduler → List repository issues → Repeat for each → Log issue title`. The action does not create, modify, or delete issues.

## Engineering features

| Concern | Implementation | Why it matters |
|---|---|---|
| Authentication | Password-masked fine-grained GitHub token (Bearer header) | Least privilege; no tokens in source code |
| Connection verification | Authenticated `GET /user` | Fails fast when credentials are wrong |
| Reusable methods | Slug validation, error formatting, issue normalization, Link parsing | Less repetition and easier testing |
| Static picklists | State, sort, sort direction | Good recipe-author experience |
| Dynamic picklists | Authenticated repository choices by owner (including token-accessible private repos), dependent labels; up to 10 pages each | Context-aware dropdowns, bounded API requests |
| One action | Read-only `List repository issues` | Focused scope; safe demonstration |
| Response schemas | Reusable object definition with nested labels | Clear downstream datapills |
| Pagination | One page per call; `next_page` from GitHub's Link header | Explicit and bounded, easy to replay |
| Error handling | Structured messages for 401/403/404/422/429/5xx; bounded, redacted 422 detail; secondary rate-limit detection | Actionable diagnosis without exposing raw responses |
| Retry behavior | Up to two SDK retries for GET server failures (500/502/503/504) | Tolerates transient failures without retrying permission errors |
| Data normalization | Excludes PRs returned by GitHub's issues endpoint | Prevents misleading issue counts |
| Input validation | Whole-number checks for page and items per page, validated owner/repo slugs | Reject malformed values before HTTP calls |
| Automated tests | 19 local, offline Ruby/Minitest tests / 59 assertions | Fast regression checks without network dependencies |

## Setup in Workato

1. Open **Connector SDK** in a personal or authorized sandbox workspace; create a **new custom connector**.
2. Name it **GitHub Issue Explorer** and paste the complete contents of [`connector.rb`](connector.rb).
3. Save and use **Test code** to check the connection, action schema, static picklists, and dependent picklists.
4. In GitHub, create a **fine-grained personal access token** restricted to your own demo repository; grant **Issues: Read-only** (and the standard metadata permission). Do not put the token in GitHub, `.env` files committed to Git, screenshots, or recipe exports.
5. In Workato, create a connection using the token. Test should authenticate using `/user`.
6. In a recipe, choose the new connector's **List repository issues** action. Enter the owner (for example, your personal username), select your demonstration repository, then choose filter values.
7. Test the action. For pagination, if `has_more` is `true`, call again using the returned `next_page` as `page`.
8. Capture screenshots only from your own demonstration account, and redact tokens, connection IDs, usernames you want private, and private issue text.

**Expected permissions:** A fine-grained token for a private demo repo needs its repository selected and the repository **Issues: Read** permission. The GitHub issues endpoint can be called unauthenticated for public repos, but this connector intentionally demonstrates authenticated access.

### Repository dropdown behavior and limits

The repository dropdown now uses authenticated `GET /user/repos`, following up to ten pages of 100 entries. It filters the results by the owner you entered, including repositories that the token can access privately. This is a **bounded list**, not guaranteed to contain all repos for accounts with more than 1,000 accessible repositories. It can also make multiple API requests when the authenticated account has many repositories.

The label dropdown follows up to ten pages of labels (up to 1,000). If the repository or label is missing, verify access rights or whether the option falls outside the scan limit. The manual input toggle may not be available in all Workato SDK editors: don't assume it exists. Both dropdowns require **live SDK verification for this revised version**.

### Pagination semantics

The GitHub `/repos/{owner}/{repo}/issues` endpoint includes pull requests. This action removes pull requests *after fetching* a single API page. Therefore `count` reflects **actual issues in that response page**, which can be fewer than `per_page`. Even `count=0` does **not** prove the batch is finished: always use `has_more` and `next_page`, determined from GitHub's `Link` header. The action deliberately does not auto-fetch all pages.

### API operations

| Intent | Request | Scope |
|---|---|---|
| Test connection | `GET /user` | Authenticated identity |
| Repository picklist | `GET /user/repos?per_page=100&page=N` | Token-accessible repositories; up to 10 pages, filtered by owner |
| Label picklist | `GET /repos/{owner}/{repo}/labels?per_page=100&page=N` | Up to 10 pages / 1,000 labels |
| Action | `GET /repos/{owner}/{repo}/issues` | Single page, 1–100 API results |

**Important pagination note:** GitHub's issues API also includes pull requests; those are excluded from output after fetching. The returned `count` is therefore the number of *issues on that page*, not the total issue count for the repository. Use `next_page` to continue; do not assume `count < per_page` means there are no more pages. Dynamic dropdowns are intentionally bounded to ten 100-item pages.

## Run local tests

Install a current Ruby and run:

```sh
ruby -c connector.rb
ruby spec/connector_test.rb
```

Current local results: **19 tests, 59 assertions, all passing**.

The tests use a tiny fake HTTP adapter to execute the connector lambdas deterministically. **They do not replace SDK runtime tests.** When you have a Workato SDK CLI environment, test the connector with the official SDK and add full integration tests (see [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md)).

## Error handling behavior

| Case | User-facing behavior | Retry? |
|---|---|---|
| Missing or malformed owner/repository | Clear input validation error before request | No |
| 401 | Reconnect invalid/expired token | No |
| 403 | Check repository permission; identify exhausted primary rate limit when header says 0 | No |
| 404 | Check owner/repository and visibility | No |
| 422 | Check filters/page; display a bounded, token-redacted GitHub message | No |
| 429 | Rate limit warning | No automatic retry |
| 500, 502, 503, 504 | GitHub transient server error; bounded Workato SDK retry | Up to 2 |
| Unexpected success response | Explicit error rather than silently accepting malformed data | No |

GitHub can enforce **secondary rate limits** through 403 responses even when the primary limit header is not zero. The connector now checks the returned message for rate-limit language, while keeping a generic permission message for other 403 errors.

## Previously observed live Workato results (previous version)

In a personal demonstration repository, a previous version of this connector returned three issues, correctly fetched page 1 and the last page with `per_page=1`, filtered the `bug` label to one issue, and rejected `per_page=101` locally. These user-observed results do **not** confirm that the revised repository and label picklist implementation works in Workato. Those checks remain open in the test plan.

## Tests and design documentation

- [`spec/connector_test.rb`](spec/connector_test.rb) — offline tests
- [`fixtures/issues_page.json`](fixtures/issues_page.json) — synthetic API response fixture
- [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md) — live verification and screenshot checklist
- [`docs/DESIGN.md`](docs/DESIGN.md) — architecture, boundaries, and tradeoffs

## Privacy and provenance

This is an **independently written demonstration**, using the public GitHub API and fictional fixtures. It does **not** contain LoanPro's code, customer data, internal schemas, Workato exports, or credentials. It is neither affiliated with nor endorsed by GitHub or Workato.

## References

- [Workato Connector SDK reference](https://docs.workato.com/en/developing-connectors/sdk/sdk-reference.html)
- [Workato picklists](https://docs.workato.com/en/developing-connectors/sdk/sdk-reference/picklists.html)
- [Workato SDK error handling](https://docs.workato.com/developing-connectors/sdk/guides/error-handling.html)
- [GitHub REST API — repository issues](https://docs.github.com/en/rest/issues/issues#list-repository-issues)
