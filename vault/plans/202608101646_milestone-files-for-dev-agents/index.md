---
title: "Per-milestone plan files handed straight to dev agents"
type: "feature"
status: in-progress
sp: 25
related_to: null
created: 2026-08-10 16:47
planned: null
started: 2026-08-10 17:36
completed: null
code_reviews: []
sessions:
- 230b182a-514b-434f-926c-e4cb0ddab343
- e6133dac-19be-4aa4-891a-dd5a6ec4bb64
retro: null
summary: Plans split into plans/{slug}/milestones/*.md — scaffold-seeded, 
  state-machine status, develop briefs paths not bodies
commit: 6da8ccabbf1010dc0d500c10b6620e7f28faf429
reviewed_at: 2026-08-10 17:32
---

# Per-milestone plan files handed straight to dev agents

## Context

A groomed plan is one document today: `{vault}/plans/{slug}/index.md` carries context, decisions, architecture and every milestone's goal, task table, per-task DoD and Verify inline. `develop`'s `develop-loop` step reads those milestone sections into runner context and hand-composes a briefing per milestone group — per-milestone request, related files, DoD, Verify, project conventions, scope boundary — which it passes as text to `booping:booping-developer`. The worker never sees the plan; it sees a lossy restatement of it, rebuilt by the runner on every group.

After this plan, groom writes each milestone as its own file under `plans/{slug}/milestones/`, and develop delegates by handing the worker two paths — the plan's `index.md` for context and scope boundary, the milestone file as the authoritative work contract. Milestone status is persisted run state on the milestone file itself, and `index.md`'s milestone table is regenerated from those files rather than hand-flipped. The observable change: a milestone is a standalone action plan any agent can execute and validate, and the runner spends no context restating it.

## Decisions

- **Granularity**: one file per milestone at `plans/{slug}/milestones/{nn}-{kebab}.md` — matches the plan's own structure and the unit develop delegates; grouping stays a develop-time concern that passes 1..N paths in one briefing.
- **Split of content**: `index.md` keeps Context, Decisions, Architecture, the surface-specific sections, Final Verification, Out of scope and CLAUDE.md impact plus a generated milestone table; milestone bodies live only in their own files — one source, no drift.
- **Standard vs template freedom**: only the milestone file's frontmatter contract (`id`, `title`, `sp`, `status`, `plan`) and three required headings (`## Tasks`, `## Definition of Done`, `## Verify`) are fixed; the rest of the body stays shaped by the chosen plan template — this is what keeps programmatic bookkeeping possible without collapsing the five templates into one.
- **Creation**: `booping scaffold` is extended to render tree *keys* through the same Jinja env that already renders file bodies, so a milestone scaffold tree keyed `{{ id }}-{{ slug }}.md` seeds each file; the alternative (a directory per milestone with a literal `milestone.md`) was rejected for path noise, and hand-written files were rejected because the frontmatter seed would be prose-specified and drift.
- **Milestone table**: regenerated from milestone frontmatter by `booping query --glob 'plans/{slug}/milestones/*.md'`, never hand-flipped; the link cell is a plain `[[wikilink]]` — an aliased wikilink needs its pipe escaped inside a table cell in Obsidian and is not worth the fragility.
- **Status**: milestone status is a real state machine — a `states: milestone` entry in `develop/playbook.yaml` with artifact `milestones/{instance}.md`, addressed as `booping playbook-transition develop <to> --state milestone --instance {nn}-{kebab}`. The `{instance}` artifact primitive and `--state`/`--instance` flags already exist; this buys a resumable per-milestone frontier from `booping playbook-state` and gives the table refresh a hook to hang on, instead of prose bookkeeping instructions in the loop body.
- **Briefing**: the worker gets paths and run-time context, never a pasted milestone body; `booping-developer`'s contract gains "read the milestone file at the given path — it is the contract".
- **No back-compat**: develop speaks only the new shape. No fallback branch, no migration of existing plans; plans already at `done` are untouched history.

## Architecture

Data flow after the change:

```
groom/draft-plan
  booping scaffold core.groom_playbook.milestone_scaffold {plan}/milestones \
      --set id=01 --set slug=cli-surface --set title="…" --set sp=3
  → plans/{slug}/milestones/01-cli-surface.md   (frontmatter seed + skeleton, body appended by the step)
  → index.md ## Milestones table, rendered from the same files by booping query

develop/provision      reads milestone frontmatter (id, title, sp, status) via query → groups
develop/develop-loop   briefing = {plan}/index.md + {plan}/milestones/{nn}-*.md paths → booping-developer
                       on report: DoD checkboxes flipped in the milestone file,
                       booping playbook-transition develop done --state milestone --instance {nn}-{kebab}
                         hook: script refresh-milestone-table {plan} → rewrites index.md's table
develop/verify         reads every milestone file's DoD + status; index.md table is derived, not authoritative
```

The milestone file is the only place a milestone's work is written down. `index.md`'s table and `booping playbook-state`'s per-instance frontier are both projections of milestone frontmatter.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 1 | Scaffold renders tree keys | 3 | done |
| 2 | Milestone file contract in config | 3 | pending |
| 3 | Plan templates carry the milestone file | 3 | pending |
| 4 | Groom writes milestone files | 3 | pending |
| 5 | Milestone state machine and table refresh | 4 | pending |
| 6 | Develop delegates paths, not bodies | 4 | pending |
| 7 | Downstream readers and documentation | 3 | pending |
| 8 | Reports, structure checks and eval fixtures | 2 | pending |

---

### M1: Scaffold renders tree keys — 3 SP | done

**Goal**: `booping scaffold` renders a tree's filename keys through the same Jinja env it already uses for file bodies, so a tree can name its files from `--set` values.

**Verify**: `just pytest booping-python/tests/commands/scaffold_test.py booping-python/tests/context/scaffold_test.py` and a manual `booping scaffold` of a templated-key tree into a tmp dir.

**Tests**: the CLI surface, parametrized — a templated key with `--set` values, a key with no template markers (unchanged), a key rendering to a name containing `/` or `..` (rejected), and the receipt/exit-code shape for each.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Render each node's name through the scaffold render env at walk time, then re-run the filesystem-safety check on the rendered name so a rendered `/` or `..` fails with the existing `ScaffoldError` path (exit 1); keys without template markers stay byte-identical. | `booping-python/src/booping/commands/scaffold.py`, `booping-python/src/booping/context/scaffold.py` | 2 | done |
| 1.2 | Tests for the rendered-key behaviour and its rejection path, matching the existing `RECEIPT_CASES` parametrized style. | `booping-python/tests/commands/scaffold_test.py`, `booping-python/tests/context/scaffold_test.py` | 1 | done |

#### Task 1.1 DoD

- [x] A tree key containing `{{ … }}` produces a file named from the rendered value, using the same env and `--set` globals as seed bodies.
- [x] A key rendering to a name with `/`, `.` or `..` exits 1 with the existing unsafe-name error, before any write.
- [x] Literal keys are unaffected — existing scaffold trees produce byte-identical output.
- [x] The receipt still prints per-path lines plus the `scaffolded N paths — …` summary.

#### Task 1.2 DoD

- [x] Parametrized cases cover: templated key, literal key, unsafe rendered name, missing `--set` variable.
- [x] Expected filenames and receipt text are written by hand in the test, never derived from the code under test.

---

### M2: Milestone file contract in config — 3 SP | pending

**Goal**: the milestone file's shape exists as schema — a scaffold tree that seeds it and a shared key describing where milestone files live and which columns project them.

**Verify**: `booping scaffold core.groom_playbook.milestone_scaffold {tmp-plan}/milestones --set id=01 --set slug=demo --set title="Demo" --set sp=3` produces the seeded file, and `booping query --glob 'plans/{slug}/milestones/*.md' --columns id,title,sp,status --sort id` lists it.

**Tests**: the config-driven surfaces — scaffolding the milestone tree into a tmp vault yields the exact frontmatter keys and headings, and a query over a two-file milestones dir returns rows ordered by `id`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add `core.groom_playbook.milestone_scaffold` — key `{{ id }}-{{ slug }}.md`, seed body carrying frontmatter `id`, `title` (tojson), `sp`, `status: pending`, `plan` and the `# M{{ id }}: {{ title }}` heading plus the three required headings as empty sections; add `milestones: {type: dir}` to `core.groom_playbook.scaffold`. | `src/config.yaml` | 2 | pending |
| 2.2 | Add the shared `core.plans.milestones` key — `glob: milestones/*.md`, `table_columns: [id, title, sp, status]` — read by both groom and develop, and a test that scaffolds the tree and queries the result. | `src/config.yaml`, `booping-python/tests/commands/scaffold_test.py` | 1 | pending |

#### Task 2.1 DoD

- [ ] Seeded milestone file frontmatter is exactly `id`, `title`, `sp`, `status`, `plan`, in that order, with `status: pending`.
- [ ] Seeded body carries `# M{id}: {title}` and the empty `## Tasks`, `## Definition of Done`, `## Verify` headings — nothing else.
- [ ] `title` goes through `tojson` like the plan scaffold's, so a colon or quote in a title cannot break the document.
- [ ] A fresh `booping scaffold core.groom_playbook.scaffold` creates `milestones/` alongside `index.md` and `request.md`.

#### Task 2.2 DoD

- [ ] `core.plans.milestones` sits directly under `core.plans` (shared by two playbooks, per the config placement rule) and is commented like its neighbours.
- [ ] No column list, glob or directory name is restated in any prompt body — they render from this key.
- [ ] The test asserts hand-written expected frontmatter and query row order.

---

### M3: Plan templates carry the milestone file — 3 SP | pending

**Goal**: all five plan templates specify a plan as `index.md` plus milestone files, so a drafted plan is written into the new shape by construction.

**Verify**: read each of the five template files and confirm the milestone-file section and checklist items are present and consistent across them — no repo gate here, and no `mdcheck` run: the structure rules that cover milestone shape are updated in M8.

**Tests**: none — prose artefacts, covered by `mdcheck` and the report snapshots in M8.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | In each template's `# Plan Body`, replace the inline `### M1: …` skeleton under `## Milestones` with the generated milestone table, and add a `## Milestone files` section specifying the per-file body shape for that surface (goal, scope and related files, tasks table, per-task DoD, Verify). | `docs/plan_templates/backend.md`, `docs/plan_templates/frontend.md`, `docs/plan_templates/cli.md`, `docs/plan_templates/claude_skill.md`, `docs/plan_templates/documentation.md` | 2 | pending |
| 3.2 | Update each `# Quality Checklist`: milestone-shape items point at the milestone file, add an item that the index table matches the milestone files, keep the `sp` rollup item true against per-file `sp`. | same five files | 1 | pending |

#### Task 3.1 DoD

- [ ] Every template names the same required frontmatter keys and the same three required headings; surface-specific guidance lives only in the free part of the body.
- [ ] No template still instructs that milestone bodies live in `index.md`.
- [ ] `documentation.md`'s milestone ordering rubric and each template's surface inserts survive the edit.
- [ ] The per-milestone `Verify` rule (scoped, no whole-repo gates) is stated once per template, in the milestone-file section.

#### Task 3.2 DoD

- [ ] Checklist items are verifiable by reading a plan directory, not by intent.
- [ ] `sp` item reads as the sum of milestone-file `sp` values.

---

### M4: Groom writes milestone files — 3 SP | pending

**Goal**: `draft-plan` seeds and writes one file per milestone and renders `index.md`'s table from them; `present` summarizes from the same source.

**Verify**: `booping render-playbook groom --step draft-plan` and `--step present` render cleanly and carry no restated column list or directory name.

**Tests**: none — prompt bodies, covered by the report snapshots in M8.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Rewrite `draft-plan`'s body: after design alignment, the step itself — no sub-step, no delegation — runs one `booping scaffold` call per milestone to seed the file, then writes that milestone's body into the seeded file with a normal file edit, authored by the step against the chosen template's milestone-file section; then it writes `index.md`'s `## Milestones` table from `booping query`. | `playbooks/groom/draft-plan/prompt.md`, `playbooks/groom/draft-plan/opus-5.md`, `playbooks/_partials/plan_templates.md` | 2 | pending |
| 4.2 | Update `present` and `cross-review` for the multi-file plan: the approval screen's milestone table comes from the same query, and the cross-review briefing names `index.md` plus the milestone files as its read set. | `playbooks/groom/present/sonnet-5.md`, `playbooks/groom/cross-review/opus-5.md` | 1 | pending |

#### Task 4.1 DoD

- [ ] The step body states the scaffold invocation once, with `--set` values, and never restates the seeded frontmatter keys.
- [ ] The body-writing mechanism is stated explicitly: scaffold seeds the file, the step writes the body into it, one milestone at a time, with no sub-step and no worker agent involved.
- [ ] `plan_templates.md` no longer says the whole body goes under `index.md`.
- [ ] The index table is described as generated output, with the query invocation given verbatim.
- [ ] The plan's `sp` frontmatter is stated as owned by the refresh script (M5.2), not hand-summed by the step.
- [ ] Milestone filenames are specified as `{nn}-{kebab}.md`, zero-padded, ordered by execution order.

#### Task 4.2 DoD

- [ ] `present`'s screen reads milestone rows from the query, not from a hand-kept list.
- [ ] The cross-review briefing's read set names both the index and the milestone files, and its return contract is unchanged.

---

### M5: Milestone state machine and table refresh — 4 SP | pending

**Goal**: milestone status is persisted run state written only by `booping playbook-transition`, and every transition refreshes `index.md`'s milestone table.

**Verify**: `just pytest booping-python/tests/commands/playbook_transition_test.py booping-python/tests/commands/playbook_state_test.py` plus a manual `booping playbook-transition develop in-progress --state milestone --instance 01-demo --workdir {tmp-plan}` and `booping playbook-state develop --workdir {tmp-plan}` showing the per-instance frontier.

**Tests**: the hook script's own surface — table replacement in an `index.md` that already has a table, one that has the heading but no table, and idempotency on a second run; plus a transition test driving `--state milestone --instance` through the new states block.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Add the `milestone` states entry to develop — artifact `milestones/{instance}.md`, initial `pending`, transitions `pending → in-progress → done`, `in-progress → blocked`, `blocked → in-progress`, each carrying the table-refresh hook. The `blocked` edge's `when` names the `**Blocked (n/2)**` attempt line develop-loop already writes, relocated into the milestone file's `## Notes`; the two-attempt abort rule stays develop-loop's prose and does not become a gate. | `playbooks/develop/playbook.yaml` | 2 | pending |
| 5.2 | Write `refresh-milestone-table` — a uv-inline Python hook script taking the plan dir, querying `core.plans.milestones`, replacing the `## Milestones` table in `index.md` in place and re-stamping the plan's `sp` frontmatter to the sum of milestone-file `sp` — with tests run by `just pytest` that invoke the script as a subprocess against a tmp plan dir. | `playbooks/develop/_scripts/refresh-milestone-table`, `booping-python/tests/scripts/refresh_milestone_table_test.py` | 2 | pending |

#### Task 5.1 DoD

- [ ] `status:` on a milestone file is written by `booping playbook-transition` only — no prompt instructs a hand-edit.
- [ ] Each transition's `when` is stated against observable milestone-file content, and `blocked` records the attempt count the loop already tracks.
- [ ] `booping playbook-state develop --workdir {plan}` reports one row per milestone instance alongside the run machine.
- [ ] The existing `run` machine's statuses and hooks are untouched.

#### Task 5.2 DoD

- [ ] The script rewrites only the block between the `## Milestones` heading and the next heading; surrounding prose is byte-identical.
- [ ] The plan's `sp` frontmatter equals the sum of milestone-file `sp` after every run — this is the only writer of `sp` after grooming.
- [ ] Running it twice in a row produces no diff the second time.
- [ ] Columns and glob come from `core.plans.milestones`, never hard-coded.
- [ ] A plan with no `milestones/` directory exits non-zero with a message naming the plan dir, and writes nothing.
- [ ] Tests run under `just pytest` and drive the script as a subprocess against a tmp plan dir.

---

### M6: Develop delegates paths, not bodies — 4 SP | pending

**Goal**: provision groups from milestone frontmatter, develop-loop briefs the worker with paths, and the worker reads its milestone file itself.

**Verify**: `booping render-playbook develop` renders cleanly; `bin/booping render src/templates/agents/booping-developer.md.j2` shows the path-based input contract.

**Tests**: none — prompt and agent bodies, covered by the report snapshots in M8.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Rewrite `develop-loop`'s briefing composition: the briefing carries the plan `index.md` path, the group's milestone file paths, the branch and project conventions, and a bounded return contract — never a pasted milestone body; bookkeeping becomes flipping DoD checkboxes in the milestone file plus the milestone transition. | `playbooks/develop/develop-loop/base.md` | 2 | pending |
| 6.2 | Update `provision` to enumerate and group milestones from `booping query` over the milestone files, and `verify` to check every milestone file's DoD checkboxes and `status: done` rather than reading `index.md`'s body. | `playbooks/develop/provision/base.md`, `playbooks/develop/verify/base.md` | 1 | pending |
| 6.3 | Update the worker agent contract: the briefing names paths, the agent reads the milestone file as its authoritative contract and the plan index for scope boundary, and its report shape stays bounded to what the runner needs. | `src/templates/agents/booping-developer.md.j2` | 1 | pending |

#### Task 6.1 DoD

- [ ] The briefing spec lists exactly: plan index path, milestone file paths, branch, conventions, return contract — written out as the literal briefing block the loop composes, so the shape is fixed rather than described.
- [ ] No instruction to inline goal, tasks, DoD or Verify text into the briefing survives.
- [ ] Milestone status flips are stated as the transition invocation with `--state milestone --instance`, and checkbox flips are stated against the milestone file.
- [ ] The one-worker-at-a-time and fresh-agent-per-group rules survive unchanged.

#### Task 6.2 DoD

- [ ] Provision's grouping table is fed by the query, and `core.sprint.max_milestones_per_agent` still bounds a group.
- [ ] Verify reads the milestone files and treats `index.md`'s table as derived.

#### Task 6.3 DoD

- [ ] The rendered agent body tells the worker which path is the contract and which is context, against the same briefing block M6.1 fixes — no new invocation flag or YAML key is introduced, only the briefing's `## Inputs` lines change.
- [ ] The worker is still barred from vault writes — checkbox and status writes stay the runner's.
- [ ] The report format stays a bounded per-milestone block.

---

### M7: Downstream readers and documentation — 3 SP | pending

**Goal**: every surface that reads a plan "in full" follows the milestone files, and the hand-authored docs describe the new shape.

**Verify**: `booping render-playbook retro --step prepare` and `booping render-playbook code-review --step review` render cleanly; `just docs`.

**Tests**: none — prompt and documentation surfaces.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Extend the plan read set in retro and code-review: `prepare`'s full-plan read, the lesson-check partial's "frontmatter, milestones, tasks, DoDs, Verify" instruction, and the review pass's DoD-checkbox cross-reference all name `index.md` plus `milestones/*.md`. | `playbooks/retro/prepare/base.md`, `src/templates/_partials/_plan_lesson_check.j2`, `playbooks/code-review/review/opus-5.md` | 1 | pending |
| 7.2 | Update the public docs and the repo guide: plan shape in the vault doc, develop's resume description, groom's plan description, README's plan-track narrative, and the CLAUDE.md Lifecycle bullet that defines a plan directory. | `documentation/vault.md`, `documentation/develop.md`, `documentation/groom.md`, `README.md`, `CLAUDE.md` | 2 | pending |

#### Task 7.1 DoD

- [ ] No surface still assumes milestone bodies live in `index.md`.
- [ ] Each read set is stated once, as a path pair, with no restated milestone anatomy.

#### Task 7.2 DoD

- [ ] `documentation/vault.md` describes the plan directory including `milestones/`.
- [ ] `documentation/develop.md`'s resume prose points at milestone status, not checkbox scanning in the index.
- [ ] CLAUDE.md's Lifecycle and Config sections name the milestone file contract and `core.plans.milestones`.
- [ ] No stale reference to the single-file plan survives in `README.md`.

---

### M8: Reports, structure checks and eval fixtures — 2 SP | pending

**Goal**: the committed playbook reports, structure rules and eval fixtures match the new plan shape.

**Verify**: `just snapshots` (diff read and reported, not accepted), `just mdcheck`, `just lint`, `just typecheck`.

**Tests**: the eval fixtures themselves — a groom fixture plan and a develop fixture plan in the new shape, so suites exercise milestone files rather than a single document.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Update the hermetic render fixture and eval fixtures to the multi-file plan shape, and adjust any `mdcheck` rule that asserts milestone structure inside `index.md`. | `playbooks/_fixtures/vault/`, `playbooks/groom/*/_fixtures/`, `playbooks/develop/*/_fixtures/`, `scripts/mdcheck.py` | 1 | pending |
| 8.2 | Run `just snapshots`, read the diff for `groom` and `develop`, and report it for the user to accept; run `just ci` minus the snapshot-accept step and fix what it surfaces. | `playbooks/groom/_reports/output.md`, `playbooks/develop/_reports/output.md` (read-only) | 1 | pending |

#### Task 8.1 DoD

- [ ] Fixture plans carry `milestones/` with at least two milestone files and a generated index table.
- [ ] `just mdcheck` passes against the rendered reports.

#### Task 8.2 DoD

- [ ] The snapshot diff is reported to the user; `just snapshots-accept` is **not** run by the worker or the runner.
- [ ] `just lint`, `just typecheck` and `just pytest` are green.

---

## Final Verification

- [ ] `just ci` green (`lint typecheck pytest snapshots mdcheck`), with the snapshot step's diff reported for user acceptance rather than accepted automatically.
- [ ] `just build` renders cleanly and `git diff -- skills/ agents/` shows only the intended agent-contract change.
- [ ] An end-to-end dry run: groom a throwaway plan in the fixture vault, confirm `milestones/*.md` exist with seeded frontmatter and a generated index table, drive one milestone transition and confirm the table refreshes.
- [ ] `booping playbook-state develop --workdir {plan}` reports the per-milestone frontier alongside the run machine.
- [ ] No rendered body restates the milestone frontmatter keys, glob or table columns — they come from `core.plans.milestones` and the scaffold tree.

## Out of scope

- No migration of existing plans and no back-compat branch in develop — plans groomed before this change are history.
- No change to the `run` state machine of groom or develop beyond the added `milestone` states entry.
- No per-milestone git branching or parallel workers — one worker at a time on the sprint branch stays the rule.
- No `query` feature work beyond what exists (no link column, no per-plan query spec); the index table's link cell is a plain wikilink written by the refresh script.
- No changes to retro, learn or code-review state machines — only their plan read sets.

## CLAUDE.md impact

- **Lifecycle** — the plan-track bullet gains the milestone-file shape (`plans/{slug}/milestones/{nn}-{kebab}.md`) and the note that milestone status is run state.
- **Config** — placement note gains `core.plans.milestones`; the scaffold-tree bullet gains rendered filename keys.
- **Playbooks** — the run-state bullet gains the `milestone` machine as an example of `{instance}` addressing.
