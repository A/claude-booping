---
id: "03"
title: "Linear provider over GraphQL"
sp: 4
status: done
plan: "plans/202608132333_task-tracker-driver-linear/index.md"
---

# M03: Linear provider over GraphQL

Every facade operation works against Linear over raw GraphQL, so `--driver linear` reads issues and writes comments, issues, sub-issues, statuses, labels and relations.

**Scope**: `booping-tracker/src/booping_tracker/providers/linear.py` plus a transport module and its fake, `booping-tracker/pyproject.toml` (adds `httpx`), `booping-tracker/tests/`. The verb surface, config resolution and receipts are M02's and do not change. No network in any test.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Write the transport: a small client wrapping `httpx` that POSTs `{query, variables}` to the configured `api_url` with `Authorization: {key}` (bare, no `Bearer` — that shape is MCP's, not the API's), reads the key from the variable named by `api_key_env`, and maps failures onto the exit-code contract: transport error, a non-empty GraphQL `errors` array, and rate limiting — which Linear returns as **HTTP 400 with code `RATELIMITED`**, so the status code alone must not be trusted — all become exit 2 with a message naming the operation. The transport is injectable so tests substitute a fake without touching the network. | `booping-tracker/src/booping_tracker/providers/transport.py`, `booping-tracker/pyproject.toml` | 1 | done |
| 3.2 | Implement the read operations: `states` via `workflowStates(filter: {team: {key: {eq: …}}})` projecting `id name type position`, and `show` via `issue(id:)` projecting identifier, url, title, state, labels, assignee and description, with `--with-comments` adding the comment connection. Both accept a human identifier or a UUID as `REF` and pass it straight through. | `booping-tracker/src/booping_tracker/providers/linear.py` | 1 | done |
| 3.3 | Implement the write operations: `comment` via `commentCreate`; `issue_create` via `issueCreate` with `teamId`, `title`, `description`, optional `parentId` for sub-issues, `labelIds` and `stateId`; `issue_update` via `issueUpdate` using `addedLabelIds` / `removedLabelIds` rather than `labelIds` so a concurrent human label edit is never clobbered; `relate` via `issueRelationCreate` with the `IssueRelationType` enum (`blocks`, `duplicate`, `related`, `similar` — note `blocked_by` is not a member, it is the inverse view of `blocks`). Label and state names from config are resolved to ids by lookup — states through the same `workflowStates(filter: {team: {key: {eq: …}}})` query task 3.2 adds, labels through `issueLabels(filter: {team: {key: {eq: …}}})` projecting `id name` — and an unmapped or unknown name exits 1 naming it and listing the team's available names. | `booping-tracker/src/booping_tracker/providers/linear.py` | 1 | done |
| 3.4 | Implement `sync`: read the artifact's frontmatter, take `status` and `tracker_issue`, map the status through `core.tracker.linear.playbooks.{playbook}.statuses`, and issue an `issueUpdate` only when the target state differs from the issue's current state — printing an `(unchanged)` receipt otherwise, so the operation is idempotent. A missing `tracker_issue` is a no-op receipt at exit 0; a status with no mapping exits 1. | `booping-tracker/src/booping_tracker/providers/linear.py` | 1 | done |

Tests: unit tests over the provider with a fake transport — one per operation asserting the GraphQL operation name, the variables sent and the mapped result, derived by hand from the documented schema, never from the provider's own query builder; parametrized error mapping (transport failure, `errors` array, HTTP 400 + `RATELIMITED`) onto exit codes; and idempotence of `sync` when the state already matches.

## Definition of Done

### Task 3.1

- [x] The request carries `Authorization: {key}` with no `Bearer` prefix, and the key comes from the env var named in config, never from a config value.
- [x] An HTTP 400 whose body carries `RATELIMITED` exits 2 with a rate-limit message, not a generic user error.
- [x] A GraphQL response carrying a non-empty `errors` array exits 2 even though the HTTP status is 200.
- [x] Tests inject a fake transport; no test performs a network call.

### Task 3.2

- [x] `states --team {key}` prints the team's states with `position`, so the caller can tell which `started` state is lowest.
- [x] `show --issue LIN-1` and `show --issue {uuid}` both work without an extra lookup query.

### Task 3.3

- [x] `issue-create --parent` produces a sub-issue whose parent is the given issue.
- [x] `issue-update --add-label` / `--remove-label` send `addedLabelIds` / `removedLabelIds`; no code path ever sends a wholesale `labelIds` on update.
- [x] `relate --type` accepts exactly the four enum members and exits 1 on anything else, naming the accepted set.
- [x] An unknown state or label name exits 1 with a message naming it and listing what the team has.

### Task 3.4

- [x] A second consecutive `sync` for an unchanged artifact sends no mutation and prints an `(unchanged)` receipt at exit 0.
- [x] An artifact whose `tracker_issue` is null exits 0 with a no-op receipt.
- [x] An artifact status absent from the status map exits 1 naming the status.

## Verify

```
cd booping-tracker && uv run pytest tests/test_linear_provider.py tests/test_transport.py
bin/booping-tracker --driver linear --config-file booping-tracker/tests/fixtures/tracker.yaml --dry-run issue-create --team ENG --title "T" --body "B" --parent LIN-1
```

Expected: the provider and transport suites pass with no network access; the dry run prints the intended `issueCreate` with its variables and performs no write.
