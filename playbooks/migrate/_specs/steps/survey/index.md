---
status: done
reviewed_at: 20260805 09:05
fixtures_reviewed_at: 20260805 09:05
suite_reviewed_at: 20260805 09:11
---

# survey

[← index](../../index.md)

## Contract

- **Needs** —
  - whether a project is attached, and where its vault lives
  - the recorded migration id — the last migration this vault applied — and whether it reads
    at all. It lives in the repo's `.booping` marker under the key `latest_migration`, and
    reaches the body as `booping.latest_migration`, the Jinja global that reads that key. A fresh vault
    records the sentinel `latest_migration: -1`, meaning nothing has been applied yet.
  - what work is currently uncommitted, across the repo and the vault
  - the pending set: every shipped migration with an id above the recorded one, each carrying
    its id, title and summary. **Injected at render time, never resolved procedurally** — the
    body carries the list already. Pinned spelling, the query surface's Jinja face:

    ```jinja
    {% set pending = 'migrations.pending' | query(where={'id:gt': booping.latest_migration}) %}
    {{ pending | as_table(columns=['id', 'title', 'summary']) }}
    ```

    `migrations.pending` is a config-declared spec addressed by dotted path, kept top-level
    rather than under `skills.migrate.queries.*` because `makemigration` consumes the same
    listing:

    ```yaml
    migrations:
      pending:
        root: core
        glob: migrations/*/migration.md
        sort: id
    ```

    `root: core` names the config tier the plugin's own files sit in, the same core → global →
    project vocabulary booping already uses; a spec omitting `root:` keeps today's
    vault-relative behaviour, so no existing spec changes. The `where` clause is supplied
    inline rather than declared, because the recorded id is only known at render time; it
    deep-merges over the spec for that call alone. `id:gt` is the ordering operator in the
    surface's clause-key suffix form, sibling of `:in` (CLI form `--where id:gt=3`) — it
    supersedes the `--where id>{booping.latest_migration}` spelling in the decisions log, which predates
    anyone reading the shipped surface. The comparison must order **numerically**, not
    lexically: `id:gt=-1` on a fresh vault has to select every shipped migration, and id 10
    has to sort after id 9.

    Three core capabilities this leans on, **none of which exist yet** — planned together in
    one downstream groom run off plan `20260805-12-35_frontmatter-query`, not split: the
    `booping` Jinja global exposing `id` from `.booping`'s `latest_migration`; the `:gt`
    ordering operator, the `where` vocabulary being `=` / `!=` / `:in` today; and the `root:`
    key, the engine globbing vault-relative today.
  - what landing a migration commits and advances, so the ask states what approval authorises
- **Value** — the run opens on solid ground and with informed consent. The ground is checked
  rather than assumed, work in flight is safe in a commit before anything is transformed, and
  the whole pending set — with what each migration will do — is on screen before the single
  approval that authorises all of them. A vault already current costs the user one line and no
  work.
- **Output files** —
  - none — this step writes no markdown. Its effects are the pending set presented in chat
    and, when the user confirmed, a commit covering the repo and the vault.
- **Harness return** — `## Changed:` empty, the step writing no file; `## Notes:` the pending
  count with each pending id, whether a commit was made, and — when the pending set is empty —
  the line that ends the run.
- **Review gate** —
  - approve applying the whole pending set — the run's only `review_gate`
  - the commit ask is **not** a gate: it is an in-body safety confirmation, asked and resolved
    inside the step, because the commit must land before the first migration runs
- **Delegation** — inline, runner-performed. Model guidance from the decomposition:
  `opus-5:medium`.

Behavioural throughout, with no git mechanics: notice uncommitted work, name what is
uncommitted, ask, and commit repo and vault on confirmation. No porcelain invocations, no
path-scoping, no override flags — how is the model's business at execution time. Migrations
transform the vault and only the vault; a repo-local vault is no special case.

## Example artifact

The step's artifact is its presentation. Pending set non-empty:

```markdown
Project `acme` is attached; its vault is at `~/Claude/acme`. The vault last applied
migration **2**.

Uncommitted work: 3 files in the repo (`src/config.yaml`, two playbook prompts) and 1 in the
vault (`plans/20260801-09-12_widget-cache/index.md`). I'd like to commit both before touching
anything, so every migration lands on a clean slate and stays independently revertable.
Shall I commit them?

**2 migrations pending:**

| id | title | summary |
| --- | --- | --- |
| 3 | Plans to directories | Convert flat `plans/{slug}.md` files into plan directories at `plans/{slug}/index.md`. |
| 4 | Targeted lessons | Move `lessons/` to `_lessons/` and add a `targets:` key to each lesson. |

They apply in id order, one at a time. Each one lands as its own commit and advances the
recorded id, so an interrupted run resumes where it stopped and any single migration can be
reverted on its own. A migration that fails stops the run there — I'll name it and propose a
fix rather than skip ahead.

Apply all 2?
```

Pending set empty:

```markdown
Project `acme` is attached; its vault is at `~/Claude/acme`. The vault last applied
migration **4**, the latest the plugin ships — **already current**, nothing to apply. Ending
the run here.
```

## Return Format

```markdown
## Changed:

## Notes:
- pending: 2 — 3 (Plans to directories), 4 (Targeted lessons)
- committed repo and vault before proceeding (user confirmed)
- approved: apply the whole pending set
```

Already current:

```markdown
## Changed:

## Notes:
- pending: 0 — already current at recorded id 4
- end the run: nothing to apply
```
