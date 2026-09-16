# booping-tracker

The task-tracker CLI. One binary, `bin/booping-tracker`, carries every interaction booping has
with an issue tracker — the playbooks and their hook scripts reach a tracker through it and
through nothing else.

One provider ships today. `cli` is the default: every verb is a receipt-printing no-op, so a
project with no tracker configured behaves exactly as it did before this binary existed. A real
tracker slots in as another provider behind the same facade, named by `core.tracker.driver`.

## Invocation

```
booping-tracker <verb> [flags]
```

Global flags, accepted by every verb:

| Flag | Meaning |
| --- | --- |
| `--driver NAME` | Override `core.tracker.driver` for this invocation. |
| `--config-file PATH` | Read the tracker config from this YAML file instead of shelling to `booping config-get` — for tests and for callers outside a vault. |
| `--output text\|json` | Receipt format. Default `text`. |
| `--dry-run` | Resolve the call, print what it would do, perform no write. Reaches no provider, so it needs no API key. |

## Verbs

| Verb | Flags | Does |
| --- | --- | --- |
| `states` | `--team KEY` | Lists the team's workflow states — position, name, type, id. The lookup you run once to fill in a status map. |
| `show` | `--issue REF` `[--with-comments]` | Reads one issue: identifier, url, title, state, labels, assignee, description. |
| `comment` | `--issue REF` `(--body TEXT \| --body-file PATH)` | Posts a comment. |
| `issue-create` | `--team KEY` `--title T` `(--body TEXT \| --body-file PATH)` `[--parent REF]` `[--label NAME]…` `[--state NAME]` | Creates an issue, or a sub-issue of `--parent`. `--label` and `--state` are names, resolved against the team. |
| `issue-update` | `--issue REF` `[--state NAME]` `[--title T]` `[--body-file PATH]` `[--add-label NAME]…` `[--remove-label NAME]…` `[--assignee REF]` | Updates an issue. Labels are added and removed discretely, never replaced wholesale, so a label a human set meanwhile survives. No flags given is a no-op receipt, not an error. |
| `relate` | `--issue REF` `--to REF` `[--type related\|blocks\|duplicate\|similar]` | Creates a relation, default `related`. |
| `sync` | `--artifact PATH` `[--playbook NAME]` | Reads the artifact's frontmatter, maps its `status:` through the configured status map, and pushes the result to the issue in `tracker_issue`. Idempotent: a second run reports `(unchanged)` and writes nothing. |

`REF` is the provider's issue identifier — a human-readable key (`ENG-123`) or a UUID.

**stdin** is not read by any verb; bodies come from `--body` or `--body-file`.

## Output

**stdout** carries the payload only. `--output text` prints one receipt line per performed
operation:

```
comment ENG-123: created (cli driver, no-op)
issue-create ENG: created (cli driver, no-op)
sync ENG-45: state "Planning" (cli driver, no-op)
show ENG-123: (cli driver, no-op)
```

`--output json` prints one JSON object carrying the operation's result fields. The `cli` provider
prints the same receipt shape with a `cli driver, no-op` suffix, so hook output stays uniform
across drivers.

**stderr** carries warnings and errors only, prefixed `error:` or `warning:` — the same
convention `booping` uses.

## Exit codes

| Code | Class | Causes |
| --- | --- | --- |
| `0` | Success | Including every `cli`-provider no-op, a `--dry-run`, and a `sync` that finds nothing to change. |
| `1` | User error | Unknown verb or flag, a missing required flag, an unknown driver name, missing or unreadable config, an unset API-key variable, an unknown team / workflow state / label / relation type, an issue that does not exist, a `--body-file` that does not, or a status with no mapping. |
| `2` | Provider error | The tracker's fault: transport failure, an error response, a malformed response, or a rate-limited request. |

The split is what lets a caller retry sensibly: `1` will fail the same way again, `2` may not.

## Configuration

The three-tier config merge stays single-sourced in booping. This binary does not re-implement
it — it shells to `bin/booping config-get core.tracker` and parses the YAML, unless
`--config-file PATH` names a file to read instead. The keys are documented in
[Project config → `core.tracker`](../documentation/project_config.md#coretracker).

Secrets are never in config. A provider's `api_key_env` holds the **name** of the environment
variable the personal API key lives in, and this binary reads that variable itself — nothing
anywhere interpolates `${VAR}` into a config value. Hook scripts inherit the full environment,
so a run invoked with the key exported has it.

That key variable is the only one this binary reads. Two more belong to its callers, not to it:
groom's step bodies fall back to `BOOPING_TRACKER_ISSUE` for the request issue ref when the ask
carries no argument, and the hook scripts honour `BOOPING_TRACKER_BIN` to point at a binary other
than `bin/booping-tracker`.

## Logging

Every invocation appends one line to `{vault}/.booping.log` in booping's existing shape,
`{ts}: [tracker {verb}] {message}`, when the cwd resolves to a vault. No vault, no line.

## Callers

1. **Hook scripts** — `playbooks/_scripts/tracker-sync` and `playbooks/_scripts/tracker-comment`,
   wired onto a playbook's transitions. Both absorb this binary's exit code and warn instead,
   because a hook failing after `status:` is written would abort the transition with the vault
   advanced and the tracker behind.
2. **You** — `booping-tracker sync --artifact {plan-dir}/index.md` is the reconcile after any
   failed mirror.

## Development

```
just lint | just typecheck | just pytest | just e2e     # both uv projects
cd booping-tracker && uv run pytest                     # this project's unit suite only
```

The unit suite runs without network. The txtar contract corpus and its conventions:
[e2e/README.md](e2e/README.md).
