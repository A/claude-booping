---
title: "Task-tracker driver layer and Linear-driven plan track"
type: "feature"
status: in-progress
sp: 21
related_to: null
created: 2026-08-13 23:33
planned: null
started: 2026-08-14 00:38
completed: null
code_reviews: []
sessions:
- d742465f-44ab-45dd-b135-b0cf799b6857
- 9dba7937-17ee-4012-b79b-21a0a56a0694
retro: null
summary: Tracker driver layer (cli + linear) so groom runs one-shot from Linear 
  issues with a persisted clarification surface
commit: f1df61c42d7c1126f43944758fc56525f2e68cef
reviewed_at: 2026-08-14 00:37
---

# Task-tracker driver layer and Linear-driven plan track

## Context

booping runs today only as one interactive Claude Code conversation. `/playbook` drives a playbook end to end: the model reads and writes vault artifacts, asks questions in chat, blocks on review gates, and persists run state only through `booping playbook-transition`. Every questioning and gating mechanism assumes a live human in the same conversation, so a `claude -p` one-shot run has nowhere to stop and nothing to resume from.

After this plan a groom run can be driven from a Linear issue instead. A new `booping-tracker` CLI, shipped as its own uv project with a provider facade, carries every tracker interaction: the `cli` provider is a no-op that keeps today's behaviour byte-identical, and the `linear` provider mirrors the plan outward and posts questions back. groom gains an `awaiting-clarification` status and a `clarifications.md` sidecar, so a run that needs the user can persist its questions, exit cleanly, and be resumed by a later invocation. Driver-conditional partials injected into groom's preamble and its steps replace `AskUserQuestion` and blocking gates with that persist-and-exit protocol whenever the tracker driver is `linear`.

The user-visible change: `bin/booping-tracker` exists as a new CLI; with `core.tracker.driver: linear` a groom run reads its request from a Linear issue, mirrors status moves onto it, writes the plan into a `plan`-labelled issue with one sub-issue per milestone cross-linked back to the request, and parks on `awaiting-clarification` with its questions posted as a comment instead of blocking on chat. With the default `cli` driver nothing changes.

The tracker agent that watches Linear and invokes `claude -p` ("hermes") already exists on the user's server and is out of scope; this plan makes booping the thing hermes can drive.

## Decisions

- **Two projects, not one**: the tracker ships as a second uv project `booping-tracker/` with `bin/booping-tracker`, a facade and one module per provider — the boundary the user asked for, keeping `httpx` and every tracker concern out of `booping-python`. Cost accepted: `just lint/typecheck/pytest/e2e` each grow a second target.
- **Config stays single-sourced in booping**: `booping-tracker` resolves `core.tracker` by shelling to `bin/booping config-get core.tracker` (YAML on stdout) rather than re-implementing the three-tier merge. `--config-file PATH` overrides it for tests and for callers outside a vault. Precedent: `playbooks/develop/_scripts/refresh-milestone-table` already shells back into `booping`.
- **Provider selection is config, not flags**: `core.tracker.driver` (`cli` | `linear`), overridable per invocation with `--driver`. An unknown driver name is a hard error (exit 1), because the config merge has no schema gate and `driver: linaer` would otherwise silently degrade to a no-op.
- **Secrets by env-var name**: config carries `api_key_env: LINEAR_API_KEY`, never a token. No `${VAR}` interpolation machinery is added anywhere — hook scripts already inherit the full environment, and the tracker reads the named variable itself.
- **The mirror never fails a transition**: a `script` hook that exits non-zero aborts `playbook-transition` *after* `status:` is already written, which would leave the vault advanced and the tracker behind. The `tracker-sync` hook script therefore absorbs the tracker's exit code, warns on stderr and exits 0; the tracker binary itself keeps honest exit codes, and re-running `booping-tracker sync` is the reconcile.
- **Vault is canonical, the tracker mirrors**: every push derives from artifact frontmatter and body. Sync is idempotent — running it twice changes nothing.
- **Raw GraphQL over `httpx`, no SDK, no MCP**: Linear ships no Python SDK and no maintained CLI (`@linear/cli` last published 2021), the official Node SDK would drag a second toolchain in, and the MCP server cannot be called from a hook. About eight operations are needed; `httpx` 0.28.1 covers them.
- **Personal API key, not an OAuth agent app**: the pilot authenticates as the user's own key with the bare `Authorization: <key>` header. Linear's agent surface (`actor=app`, `delegateId`, agent sessions, `elicitation` activities) models clarification natively and is the obvious later upgrade, but it belongs with hermes, which is out of scope.
- **Issue type is a label**: Linear has no issue-type concept in 2026 — the SDL only mentions `issueType` inside its Jira integration types. `request` and `plan` are label names carried in `core.tracker.linear.playbooks.groom.labels`.
- **Status mapping is per playbook, per status**: `core.tracker.linear.playbooks.{playbook}.statuses` maps a playbook status to a Linear workflow-state name. Linear states are presentational and are never read back as run state.
- **`awaiting-clarification` is a real status with static return edges**: entered from `framing` and from `drafting`, each entering edge carrying its own `frontmatter-update return_to={status}` hook, with one return edge per source. A hook value cannot be computed from the transition, so the mapping is static per edge — which also keeps the frontier report readable.
- **Clarifications live in a sidecar, not frontmatter**: `clarifications.md` beside `index.md`, one H2 per question carrying an id and an `open`/`answered` state, with free markdown under `**Answer:**` so multi-line answers are natural. Mirrors develop's `feedback.md` precedent, and the file is postable to Linear verbatim.
- **Injection is per body, not global**: `AskUserQuestion` is hard-wired into individual step bodies, so a preamble partial alone does not reach them. groom's preamble gets the protocol partial; `intake` and `present` get their own conditional blocks. The shared driving protocol in `src/templates/_partials/_playbook_driving.j2` is left untouched — changing it would alter every interactive run.
- **The request issue reaches the run through the ask, with an env fallback**: hermes composes `claude -p "/playbook groom LIN-123"`, so the ref is the playbook's argument — the same channel an interactive user would use. `BOOPING_TRACKER_ISSUE` is read only when the ask carries no ref, which is what lets a hook or a bare resume find the issue. A `linear` driver with neither available is a hard stop reported to the caller, never a guess.
- **`tracker_provider` records the resolved driver name** (`linear`), so an artifact says which surface it was mirrored to even after config changes.
- **Pilot scope is groom only**: develop, retro and code-review keep their interactive-only behaviour; their statuses are not mapped and their bodies are not touched.

## Architecture

Two binaries, one config, one direction of truth.

`bin/booping-tracker` is a thin shell exec'ing `uv run --project booping-tracker booping-tracker "$@"`, mirroring `bin/booping`. Inside, `booping_tracker/cli.py` parses the verb, `booping_tracker/config.py` resolves `core.tracker` (via `bin/booping config-get` or `--config-file`), and `booping_tracker/facade.py` defines the operation set every provider implements: `states`, `show`, `comment`, `issue_create`, `issue_update`, `relate`, `sync`. `providers/cli.py` implements all of them as receipts-only no-ops; `providers/linear.py` implements them against `https://api.linear.app/graphql` through an injectable transport, which is what makes the provider testable without network.

Callers are three:

1. **Hook scripts** — `playbooks/_scripts/tracker-sync` and `playbooks/_scripts/tracker-comment`, wired onto groom's transitions in `playbooks/groom/playbook.yaml`. They run with cwd set to the plan directory and inherit `LINEAR_API_KEY` plus `BOOPING_ARTIFACT` / `BOOPING_WORKDIR` from `playbook-transition`. Both absorb the tracker's exit code.
2. **Step bodies** — under `core.tracker.driver: linear`, the injected partials tell the model to call `bin/booping-tracker show` to read the request issue, `issue-create` for the plan issue and its milestone sub-issues, `relate` to cross-link plan and request, and `bin/booping frontmatter-update` to record the resulting refs.
3. **The user, by hand** — `booping-tracker sync --artifact …` as the reconcile after any failed mirror.

Run-state flow for a clarification round-trip: a step raises questions, writes them into `clarifications.md`, and takes `booping playbook-transition groom awaiting-clarification`. The edge's hooks stamp `return_to`, post the sidecar as a comment on the request issue, and move the Linear issue into the mapped presentational state; the run then ends. The next `claude -p` invocation starts from `booping playbook-state groom --workdir {plan-dir}`, reads `awaiting-clarification` plus `return_to`, reads the answers back out of `clarifications.md`, and transitions back to the recorded status.

New frontmatter on `index.md`, seeded by the groom scaffold and written only through `booping frontmatter-update`: `tracker_provider`, `tracker_request` (the source request issue) and `tracker_issue` (the plan issue). `return_to` is hook-written and never hand-edited.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Tracker config surface](milestones/M01-tracker-config-surface/M01-tracker-config-surface.md) | 2 | done |
| 02 | [booping-tracker project and cli provider](milestones/M02-tracker-project-skeleton/M02-tracker-project-skeleton.md) | 3 | done |
| 03 | [Linear provider over GraphQL](milestones/M03-linear-provider/M03-linear-provider.md) | 4 | done |
| 04 | [Mirror hooks on groom transitions](milestones/M04-mirror-hooks/M04-mirror-hooks.md) | 3 | done |
| 05 | [awaiting-clarification status and clarifications sidecar](milestones/M05-clarifications-status/M05-clarifications-status.md) | 3 | done |
| 06 | [Driver-conditional prompt injection into groom](milestones/M06-driver-injection/M06-driver-injection.md) | 4 | pending |
| 07 | [Docs, CLAUDE.md and report consistency sweep](milestones/M07-docs-and-consistency/M07-docs-and-consistency.md) | 2 | pending |

## I/O contract

**Invocation**: `booping-tracker <verb> [flags]`.

Global flags, accepted by every verb: `--driver cli|linear` (overrides `core.tracker.driver`), `--config-file PATH` (read the tracker config from this YAML file instead of shelling to `booping config-get`), `--output text|json` (default `text`), `--dry-run` (resolve and print the intended call, perform no write).

| Verb | Arguments | Does |
| --- | --- | --- |
| `states` | `--team KEY` | Lists the team's workflow states — id, name, type, position |
| `show` | `--issue REF` `[--with-comments]` | Reads one issue: identifier, url, title, state, labels, assignee, description |
| `comment` | `--issue REF` `(--body TEXT \| --body-file PATH)` | Posts a comment |
| `issue-create` | `--team KEY` `--title T` `(--body TEXT \| --body-file PATH)` `[--parent REF]` `[--label NAME]…` `[--state NAME]` | Creates an issue, or a sub-issue when `--parent` is given |
| `issue-update` | `--issue REF` `[--state NAME]` `[--title T]` `[--body-file PATH]` `[--add-label NAME]…` `[--remove-label NAME]…` `[--assignee REF]` | Updates an issue; labels are added and removed discretely, never replaced wholesale |
| `relate` | `--issue REF` `--to REF` `[--type related\|blocks\|duplicate\|similar]` | Creates an issue relation, default `related` |
| `sync` | `--artifact PATH` `[--playbook NAME]` | Reads the artifact's frontmatter, maps its `status` through the configured status map, and pushes state (and body, for the plan issue) to the issue named by `tracker_issue` |

`REF` is a Linear human identifier (`LIN-123`) or a UUID; both are accepted by the API directly, so no lookup round-trip is needed.

**stdin**: not read by any verb. Bodies come from `--body` or `--body-file`.

**stdout**: the payload only. `--output text` prints one receipt line per performed operation (`comment LIN-123: created https://…`, `sync LIN-45: state "Planning" (unchanged)`); `--output json` prints one JSON object with the operation's result fields. The `cli` provider prints the same receipt shape with a `cli driver, no-op` suffix, so hook output stays uniform across drivers.

**stderr**: warnings and error messages only, prefixed `error:` or `warning:` per the existing `booping` convention.

**Exit codes**: `0` success, including every `cli`-provider no-op and a `sync` that finds nothing to change. `1` user error — unknown driver, missing or unreadable config, unset API-key variable, unknown verb or flag, a status with no mapping, a `--body-file` that does not exist. `2` provider error — network failure, GraphQL error response, or a rate-limited request (Linear returns `RATELIMITED` as HTTP 400, so status code alone must not be trusted).

**Environment**: `LINEAR_API_KEY` (the variable named by `core.tracker.linear.api_key_env`) supplies the token, and `BOOPING_TRACKER_ISSUE` optionally supplies the request issue ref when a caller has no way to pass one as an argument. Nothing else is read from the environment.

**Logging**: every invocation appends one line to `{vault}/.booping.log` in the existing `{ts}: [tracker {verb}] {message}` shape when a vault resolves; no-op otherwise.

## Final Verification

- [ ] `just ci` green — lint, typecheck, pytest, snapshots, mdcheck and e2e, across both uv projects.
- [ ] `bin/booping-tracker --help` and every verb's `--help` reflect the I/O contract above.
- [ ] With no `core.tracker` configured at all, `bin/booping render-playbook groom` output is unchanged from the committed report, and a full interactive groom run behaves exactly as before.
- [ ] Manual pilot against real Linear with `LINEAR_API_KEY` set and `core.tracker.driver: linear` in the vault config: a `request`-labelled issue drives one groom run through to a `plan`-labelled issue with milestone sub-issues, cross-linked to the request, with at least one round-trip through `awaiting-clarification`.
- [ ] Re-running `booping-tracker sync --artifact {plan-dir}/index.md` twice produces the same receipt and changes nothing on the second run.

## Out of scope

- **hermes itself** — webhook intake, dispatch, retry, dedup, `claude -p` invocation and its flags. booping ships no runner; hermes composes the command.
- **develop, retro and code-review tracks** — no status maps, no injected partials, no sub-issue status mirroring. Sibling plans.
- **Linear agent surface** — OAuth app with `actor=app`, `delegateId` delegation, agent sessions, `elicitation` activities with selectable options, and agent attribution on comments. A later upgrade of the same provider.
- **Linear MCP server** — not configured, not used; the model reaches Linear only through `booping-tracker`.
- **Jira or any second provider** — the facade is shaped for one, but only `cli` and `linear` are implemented.
- **User playbooks** — the injected partials are written for core groom only.
- **Reading Linear as run state** — Linear workflow states are written, never read back to decide a transition.
- **Bidirectional body sync** — a human editing the plan issue's body in Linear is not merged back into the vault.

## CLAUDE.md impact

- `## Commands` — the new `bin/booping-tracker <verb> --help` entry point, and the `just` targets that now cover two projects.
- `## Layout` — `booping-tracker/` as a second uv project, and its `e2e/` corpus.
- `## Config` — `core.tracker` placement, the `api_key_env` convention, and the fact that no config value is env-interpolated.
- `## Playbooks` — the tracker hook scripts in `playbooks/_scripts/` and driver-conditional prompt injection.
- `## Lifecycle` — groom's new `awaiting-clarification` status, the `clarifications.md` sidecar and the `return_to` key.
