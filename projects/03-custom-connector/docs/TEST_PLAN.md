# Verification plan — Workato sandbox

Do not mark a checkbox until tested. No real token or customer data belongs in the repository.

## Connector SDK tests

- [ ] Save the **revised** connector.rb in Workato with no validation errors.
- [ ] Revalidate the connection using the **revised** connector with a valid fine-grained token.
- [ ] Connection test fails with an invalid token and displays a useful message.
- [ ] Static state and sort dropdowns load.
- [ ] Entering an owner loads token-accessible repositories (including any private test repo) into the dependent dropdown.
- [ ] Selecting a repository loads its labels into the dependent label dropdown.
- [ ] Verify repository picker behavior for private repos; do not depend on manual entry.
- [ ] List issues works with a demo repository containing several fictional issues.
- [ ] A pull request in the test repository is not included in the returned issues list.
- [ ] A test repository with > page size results returns next_page/has_more accurately.
- [ ] The next page does not repeat first-page results.
- [ ] Verify `per_page=101`, `page=0`, `page="1junk"`, `per_page="2.5"` produce clear local validation errors.
- [ ] Verify 422 details are helpful and do not echo secrets; verify 404/permission errors separately if practical.
- [ ] Verify results of retry on a simulated 5xx response in SDK test setup.
- [ ] Verify repository and label dropdown pagination in a sandbox account with more than 100 results (or use mocked API tests).
- [ ] Verify issue pagination when the response contains pull requests; `count` must exclude PRs but `has_more` must use the Link header.

## Evidence for portfolio

- [ ] Screenshot: successful connection (no token shown).
- [ ] Screenshot: dependent repository and label picklists.
- [ ] Screenshot: action configuration (owner, repository, state, page size).
- [ ] Screenshot: test result with sample issue list and pagination metadata.
- [ ] Screenshot: intentional 404 / permission failure with clear error.
- [ ] Update the README verification status to describe exactly what passed.
- [ ] Do not describe any unverified item as tested or production ready.

## Verified before this revision

The previous connector version was tested live with 3 demo issues: basic retrieval, page 1/last page with `per_page=1`, filtering by `bug`, and local rejection of `per_page=101`. These are **not yet rerun** against the revised connector. Offline tests of the revised connector are passing (19 tests, 59 assertions).
