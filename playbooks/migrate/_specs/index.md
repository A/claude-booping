---
status: done
reviewed_at: 20260805 08:41
playbook_yaml_reviewed_at: 20260805 08:52
regress: skip
---
# migrate — Decomposition

Bring a vault up to the current booping format by applying every pending migration the plugin
ships, in id order, on one up-front approval. Migrations transform **the vault and only the
vault** — a repo-local vault is no special case, it merely happens to live inside the repo tree.
`survey` opens the run: it checks the ground (project attached, recorded id readable), offers to
commit work in flight, presents the pending set the rendered body already carries, and asks the
run's single question; then the `apply` subgraph runs once per pending migration, each instance
completing the whole cycle — apply, advance the recorded id, commit everything — before the next
starts; `summarize` closes with one report. Because the pending list is injected at render time
through the query surface's Jinja face rather than computed procedurally, the playbook is
`jinja: true` (and therefore `requires_project: true`). The run is ephemeral: the migration id in
the repo's `.booping` marker is the only state, advanced per migration, so an interrupted run
resumes by re-reading it and a current vault is a no-op.

## Graph

```yaml
graph:
  survey: []
  apply:
    dependencies: [survey]
    repeat: once per pending migration, in ascending id order; strictly one instance at a time — never in parallel — and a failed instance stops the run
    graph:
      apply-migration: []
  summarize: [apply]
```

`apply-migration` carries **no** `detached:` key, and that absence is load-bearing: the driving
protocol runs subgraph instances in parallel only when every inner step is detached, so a
runner-performed inner step makes strict sequencing structural rather than a promise in prose —
and puts halt-on-failure in the runner's own hands. Context-fresh isolation is then bought inside
the step body, which spawns a sub-agent per migration (see its Delegation cell).

## Steps

| Step | Summary | Inputs | Artifact | Gate | Delegation | Model | Spec |
| --- | --- | --- | --- | --- | --- | --- | --- |
| survey | open the run: confirm a project is attached and the recorded id is readable; when work is uncommitted, say what is uncommitted, ask, and commit repo and vault on confirmation; present the pending set the rendered body carries and what each migration will do; report "already current" and end the run when the set is empty | attached project and its vault location; the recorded migration id; what work is currently uncommitted; the pending set with each migration's id, title and summary, injected at render time; what landing a migration commits and advances | committed repo and vault when the user confirmed; the pending list presented in chat | approve applying the whole pending set — the run's only `review_gate`; the commit ask is an in-body safety confirmation, not a gate, since it must commit inside the step | inline | opus-5:medium | [spec](steps/survey/index.md) |
| apply-migration | run one migration's whole cycle: hand its `migration.md` — prompt plus commands — verbatim to a context-fresh sub-agent, then advance the recorded id and commit everything, or halt the sequence naming the failing id, what failed and a remedy the user can apply by hand | one migration's location, so the sub-agent reads the prompt and commands itself; the sub-agent's outcome receipt; the vault's current on-disk state; where the recorded id lives | the vault files that migration transforms; the advanced recorded id; one commit per migration covering the whole working state | none — per-migration gates are excluded by design; halting is a failure path, and this step owns it | assisted — runner-performed (no `detached:` key, which is what forbids parallel instances), body delegates the migration itself to a fresh sub-agent it briefs with the migration's location, so no migration body ever enters the runner's context. A deliberate widening of the documented assisted level, which delegates only heavy reads to the researcher: here the delegated work is the migration's execution, and the body must spell out the bootstrap and return contract the framework would otherwise supply to a `detached:` step | opus-5:medium | [spec](steps/apply-migration/index.md) |
| summarize | close with a single report of what changed across the whole run | each applied migration's id and outcome; the resulting recorded id; the commits made; whether the vault is now current | none — one closing summary in chat | none | inline | sonnet-5:medium | [spec](steps/summarize/index.md) |

## Questions

- [x] ~~Which id is authoritative — the `NNN_` directory prefix or the `id` frontmatter key —
      and what happens when they disagree?~~ — settled: **frontmatter wins, the prefix is never
      read**. `id:` in `migration.md` is the single source of truth the query surface filters and
      sorts on; the directory prefix is a cosmetic sort hint for anyone browsing `migrations/`.
      There is no disagreement to detect, so no step checks for one. Consequences: migration
      directories can be renamed freely, and `makemigration` must write the id into frontmatter
      (the prefix it also writes carries no meaning).
- [x] ~~Direction of the pending-set filter.~~ — settled: **greater than**,
      `--where id>{booping.latest_migration}`. `booping.latest_migration` is the last-applied id; pending is every shipped
      migration with a higher id (recorded 2, shipped 1–4 → pending 3, 4). The brief's `<` was a
      slip. The downstream core plan must therefore grow `--where` an ordering operator that
      supports `>` on the id.
- [x] ~~Clean-tree preflight when the vault is repo-local.~~ — settled by **reframing**; all
      three candidates rejected. Migrations touch the vault and only the vault, so there is no
      "which tree must be clean" question — a repo-local vault is still just the vault. Nothing
      enforces cleanliness and nothing refuses: `survey` names work in flight, asks, and commits
      both repo and vault on confirmation, and each migration's own commit likewise covers the
      whole working state. Stated behaviourally throughout — no git mechanics, no path-scoping,
      no override flag; detection and committing are the model's business at execution time.
