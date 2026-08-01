# Write the playbook manifest

The input is the confirmed decomposition plus two answers: the target model and the
destination root. Produce the **manifest** — the playbook's structure
(`playbook.yaml`) and identity (`playbook.md`) as two small files, where model and root
become concrete before any step dir carries them.

## The files to write

`<name>/playbook.yaml` — the structure:

- `graph:` copied EXACTLY as the confirmed decomposition orders it — no rename, no reorder.
- when the decomposition carries `## States`: top-level `state: <name>` naming the outer
  machine, `state:` inside each subgraph node the section assigns one, and `states:`
  translated row-for-row — per machine `artifact` from its artifact line, `initial` from the
  `none` row's To, one `statuses.<state>` entry per source state with
  `transitions: [{to, when, gates, hooks}]` cells copied verbatim (Hooks cells are already
  machine-readable — never paraphrase), `terminal: true` for `ᵗ` states, superstate rows
  becoming `superstates`.
- no `## States` → graph-only playbook.yaml.

`<name>/playbook.md` — the identity:

- frontmatter: `name`, `title`, `summary`, `trigger` (the user's terms — never internal step
  names), `jinja: true`. Add `requires_project: true` only when steps write into a booping
  project. Never `graph:` — playbook.yaml owns structure.
- body: minimalistic. The renderer injects the execution graph, step summaries and gates from
  `graph:` and step frontmatter — the body never lists steps, waves or gates. It carries only
  the lead (what a run produces), fan-out or one-at-a-time instructions for repeated work,
  orchestrator decisions the whole run honors, and the eval-run rules: which tier the harness
  runs and when — steps themselves never launch one.

## Return format

```
## Changed:
- [CREATED] <name>/playbook.yaml
- [CREATED] <name>/playbook.md

## Notes:
```
