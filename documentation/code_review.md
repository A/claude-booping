# code-review playbook

Code review is a **playbook**, not a skill. Run it with:

```text
/playbook code-review
```

A run reviews one confirmed scope end to end — `scope` settles what to look at (any `done` plan, the latest commits, or a named target) and opens the run's artifact, `review` returns severity-classified findings from a detached pass, `present` writes them to the artifact and collects your verdict, and `resolve` acts on that verdict and closes the run.

## The review artifact

Every run writes one file under the vault's `codereviews/`: `codereviews/{plan-dirname}/{YYYYMMDDHHmm}.md` when a plan is in scope, `codereviews/{target-slug}/{YYYYMMDDHHmm}.md` for an ad-hoc scope. It holds `## Scope`, `## Findings`, `## Verdict` and `## Resolution`, and its frontmatter carries `plan:` — the reviewed plan's vault-relative path, or `null` when nothing was in scope.

That artifact is the run's own state, so a stopped review is **resumable** and a second look after fixes is a new, separately recorded run.

## Statuses

The status vocabulary is declared in `playbooks/code-review/playbook.yaml`'s `states:` block and lives in the artifact, never in the reviewed plan:

- **`in-agent-review`** — the artifact is open and the detached pass is producing findings.
- **`human-review`** — the findings are on record and your verdict is pending.
- **`done`** — every finding is resolved (applied, delegated or dropped) and recorded.

The machine declares no `artifact:` key, so the run works from the vault root and is addressed explicitly: `booping playbook-state code-review --workdir {vault} --target codereviews/{dir}/{ts}.md`.

Closing the run stamps `reviewed_at` on the artifact and runs the `close-code-review` hook, which appends the artifact's path to the reviewed plan's `code_reviews:` list and commits the vault. An ad-hoc review (`plan: null`) skips the append and just commits. The plan's own `status:` is never touched.

## The queue

`scope` offers every plan at `status: done`, listed with its `code_reviews:` history — a reviewed plan stays on the list, so re-reviewing is first-class rather than an exception. See `core.code_review_playbook.queries.scope_candidates` in [Project config](project_config.md).

See [Playbooks → Shipped playbooks](playbook.md#shipped-playbooks) for how playbooks are driven, and [Vault → `review_templates/`](vault.md#review_templates) for project-local review checklists.
