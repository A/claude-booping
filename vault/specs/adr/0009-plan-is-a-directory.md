---
type: adr
title: A plan is a directory whose index.md is both plan and run artifact
summary: A plan lives in plans/{slug}/; index.md is the plan document and the machine's artifact at once, and run sidecars sit beside it — no separate plan.md and no _runs/ workdir.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [values/0001#single-source, values/0001#quality-at-a-rational-cost, values/0001#everything-in-one-place]
sources: [playbooks/groom/_specs/DECISIONS.md, vault/notes/20260802-groom-skill-vs-playbook-metrics.md, playbooks/migrate/_specs/DECISIONS.md, CHANGELOG.md, CLAUDE.md]
---

## Context

Plans were flat files `plans/{slug}.md`. The groom playbook needed a run workdir and
a machine artifact. It first used a workdir-local `run.md` under `_runs/` whose edge
hooks stamped the plan file, then a plan directory with two documents: `plan.md`
(the executable plan) and `index.md` (the machine artifact and evolving run
document). The skill-versus-playbook measurements found the dual artifact a root
cause of the playbook's cost: content authored twice, 21 Edits, late singleton
edits at 130–157k context. Making `index.md` the only document cut the edits from
21 to 2.

## Decision

A plan is the directory `plans/{slug}/`, which is also the run workdir. Its
`index.md` is both the plan document and the machine's artifact. Run sidecars sit
beside it: `request.md` (the framing brief), `research.md` (only when web research
was requested), `clarifications.md`, and the milestone directories. The discovery
shape is the `core.plans.glob` config key. Flat plan files are converted by the
migration `001_vault_layout`.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Directory with one index.md](#directory-with-one-indexmd) | accepted | medium | low | One document; sidecars beside it |
| [Flat plan file](#flat-plan-file) | rejected | low | medium | No home for run sidecars |
| [Directory with plan.md and index.md](#directory-with-planmd-and-indexmd) | rejected | medium | high | Content authored twice |
| [A separate runs workdir](#a-separate-runs-workdir) | rejected | medium | high | Run and plan split; hooks stamp across |

### Directory with one index.md

The plan document carries the run status; everything else the run writes is a
sidecar.

- **Pros:** one file to author and to read; the run resumes from the plan itself;
  groom and develop continue on the same file.
- **Cons:** every plan consumer had to change from the flat glob; a migration for
  existing vaults.
- **Complexity:** medium.
- **Reversibility:** low.

### Flat plan file

`plans/{slug}.md`.

- **Pros:** simplest layout.
- **Cons:** research, briefs and milestone files have nowhere to live beside it.
- **Complexity:** low.
- **Reversibility:** medium.

### Directory with plan.md and index.md

The executable plan and the run document as two files.

- **Pros:** the plan stays free of run bookkeeping.
- **Cons:** measured: content authored twice and 21 Edits against 2.
- **Complexity:** medium.
- **Reversibility:** high.

### A separate runs workdir

A `run.md` in a separate workdir; hooks stamp the plan file by path.

- **Pros:** the plan file stays untouched by the procedure.
- **Cons:** two locations per run; a subgraph had to dissolve to make it work.
- **Complexity:** medium.
- **Reversibility:** high.

## Consequences

- `index.md`'s `## Milestones` table and the plan's `sp` are generated from the
  milestone files, not hand-kept.
- Plans groomed before this layout need the migration before develop can read them.
