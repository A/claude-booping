# code-review playbook

Code review is a playbook driven by `/playbook`, the plugin's single skill and the only way to start a review:

```text
/playbook code-review
```

A run reviews one confirmed scope end to end: `scope` settles what to look at (any `done` plan, the latest commits, or a named target) and opens the artifact, `review` returns severity-classified findings from a detached pass, `present` writes them and collects your verdict, `resolve` acts on it and closes the run.

## The review artifact

Every run writes one file under the vault's `codereviews/`: `codereviews/{plan-dirname}/{YYYYMMDDHHmm}.md` when a plan is in scope, `codereviews/{target-slug}/{YYYYMMDDHHmm}.md` for an ad-hoc scope. It holds `## Scope`, `## Findings`, `## Verdict` and `## Resolution`, and its frontmatter carries `plan:` — the reviewed plan's vault-relative path, or `null` when nothing was in scope.

The artifact is the run's own state: a stopped review is **resumable**, and a second look after fixes is a new, separately recorded run.

## Statuses

The status lives in the artifact, never in the reviewed plan:

- **`in-agent-review`** — the artifact is open and the detached pass is producing findings.
- **`human-review`** — the findings are on record, your verdict is pending.
- **`done`** — every finding is resolved (applied, delegated or dropped) and recorded.

The run works from the vault root and addresses the review file explicitly; a stopped run resumes with `booping playbook-state code-review --workdir {vault} --target codereviews/{dir}/{ts}.md`.

Closing the run stamps `reviewed_at` on the artifact, appends the artifact's path to the reviewed plan's `code_reviews:` list, and commits the vault. An ad-hoc review (`plan: null`) skips the append and only commits. The plan's `status:` is never touched.

## The queue

`scope` offers every plan at `status: done`, listed with its `code_reviews:` history — a reviewed plan stays on the list, so re-reviewing is first-class. See `core.code_review_playbook.queries.scope_candidates` in [Project config](project_config.md).

## Review templates

Review checklists are markdown files in `review_templates/`, layered core → global → project: the plugin ships a core set, your global home directory adds machine-wide ones, your vault's `review_templates/` holds the project's own. A later level overrides an earlier one by name. See [Vault → `review_templates/`](vault.md#review_templates) for the project-level directory.

See [Playbooks → Shipped playbooks](playbook.md#shipped-playbooks) for how playbooks are driven.
