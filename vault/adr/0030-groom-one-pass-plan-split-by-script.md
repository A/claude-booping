---
type: adr
title: Groom drafts one plan in stages; a script cuts it into milestone files
summary: Proposed — groom is one staged draft (V3a) without the 16 self-followed rules; `booping plan split` cuts the one-file plan on headings into milestone files.
created_by: claude
created_at: 2026-10-16
updated_at: 2026-10-16
status: proposed
values: [value/0012, value/0002, value/0015, value/0010]
issues: []
sources: [vault/idea/0003-groom-depth-scales-with-task.md]
---

## Context

The current groom playbook (V0) spends 13–23 minutes and $4.25–5.62 per plan across many detached
steps. A benchmark in `booping-benchmarks/groom` (idea/0003) ran variants on six past tasks in
isolated environments; round 2 judged 12 plans per task (V2, V3, V3a, V5 × 3) on s1 (small), m2
(medium) and c1 (complex) with codex and a neutral `claude -p`, no rubric and no final solution,
plus a mechanical incidents metric (what a plan would have prevented of what really went wrong).

| Variant | Mean judge score (6 cells) | Incidents s1 / m2 | Cost / time per plan |
|---|---|---|---|
| V3 — template + research → draft → self-review | 6.7 | 73% / 70% | $3.09 / 9.1 min |
| V3a — V3 without self-review | 6.6 | 72% / 62% | $2.75 / 7.9 min |
| V2 — template only | 5.8 | 70% / 62% | $2.92 / 8.9 min |
| V5 — V3 + 5 rules kept from the old groom | 5.3 | 65% / 52% | $2.62 / 7.1 min |

Only the staged variants found m2's hidden defect (the gateway truncates a take at 60 s, confirmed
against the code by codex and Gemini); spread inside one variant (V3 scored both 9 and 4 on s1) is
larger than between V3 and V3a. A rule ablation on V3 (45 rules in 9 batches, 40 runs,
`groom/ablation/report.md`) found 16 rules the model follows without being told, 16 carried by the
template's sections, and 9 milestone-shape rules it misses even when told (36–58%).

Develop needs milestone files (`milestones/M{nn}-*/`) for per-milestone status, feedback and
delegation, and packs them into briefings by SP (adr/0022). Models writing those files directly
drift: in the split benchmark (`groom/split/report.md`, 12 single-file plans) Haiku rewriting the
plan passed every threshold on 6/12, Haiku mapping line ranges for a script on 8/12, Sonnet on
12/12 at $0.71 — and a script cutting on the plan's own headings on 12/12 at $0 in under a second.

## Criteria

- Plan quality at least that of V3 on the benchmark tasks.
- Cost and wall time well under V0's.
- Groom's output contract unchanged: `index.md` plus one file per milestone, as develop reads today.

## Decision

1. **Groom is V3a.** One drafting pass on the plan template with two stages, research then draft;
   no separate self-review step. The 16 rules the ablation shows the model follows unprompted and
   the anti-pattern list leave the prompt; the template's sections stay.
2. **The plan is drafted as one file.** Milestones are level-3 headings `### M{nn} — <title>` under
   one milestones section, each with `sp:` and `depends_on:` and the sub-headings Tasks, Definition
   of Done, References, Verify. The prompt fixes this format.
3. **`booping plan split` cuts it.** A deterministic command cuts the plan on those headings, byte
   for byte, into `index.md` and the milestone files, writes the milestone table and the SP groups
   (adr/0022), and never splits a code fence. It exits non-zero when the plan has no milestone
   headings and flags a milestone without `sp`; only then a model (Sonnet) splits the plan.
4. **The milestone contract is checked after the split**, not asked for in prose: one Verify
   command, named files, DoD per task. A failing milestone goes back to the draft with the finding.

Out of this decision, own follow-ups: the milestone file name `milestones/M{nn}-*/index.md`
(owner, 2026-10-16) and a light path for small, already-decided requests (idea/0003, corpus case
`s3-booping-specs-site-registries`).

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [V3a plus script split](#v3a-plus-script-split) | proposed | medium | high | Best quality per cost; contract unchanged |
| [V3 with self-review](#v3-with-self-review) | rejected | medium | high | +0.1 points for +12% cost and +15% time |
| [Model writes the milestone files](#model-writes-the-milestone-files) | rejected | low | high | Haiku edits text; Sonnet costs $0.71 a plan for what a script does |
| [Keep the current groom](#keep-the-current-groom) | rejected | low | high | Twice the time and cost; judged lower on s1 and m2 |

### V3a plus script split

The decision above.

- **Pros:** quality on par with V3; about 2× faster and 1.7× cheaper than V0; the split is free,
  exact and testable; develop, `budget.py` and the worker agents keep reading the same files.
- **Cons:** the plan format becomes a hard contract for the drafting model; judged on three tasks
  with n = 3 per variant.
- **Complexity:** medium — prompt rewrite, a new command, a contract check.
- **Reversibility:** high — the old playbook stays in git.

### V3 with self-review

The same drafting pass with a self-review stage at the end.

- **Pros:** highest mean score, best incidents on m2.
- **Cons:** the gain over V3a is inside the noise; the step costs money and time on every plan.
- **Complexity:** medium.
- **Reversibility:** high.

### Model writes the milestone files

A model reads the one-file plan and writes the milestone files itself.

- **Pros:** no format contract for the drafting step.
- **Cons:** Haiku rewrites text on long plans (coverage down to 95%, invention up to 4.5%); line
  maps drift by 1–2 lines; Sonnet passes but costs $0.71 and 4.6 minutes per plan.
- **Complexity:** low.
- **Reversibility:** high.

### Keep the current groom

The multi-step groom playbook as it is (V0).

- **Pros:** no work.
- **Cons:** 13–23 minutes and $4.25–5.62 per plan; last on s1 and m2 in round-1 judging (codex ranked it
  first on c1).
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- `playbooks/groom` is rewritten around one drafting step; `_partials/milestone_contract.md` turns
  into the post-split check; `plan_templates.md` states the heading format.
- New `booping plan split` with e2e cases on real plan shapes, including the 12 benchmark plans.
- Snapshot reports of groom change; develop, `budget.py`, `pi-developer`, `booping-developer` and
  `develop-pi` stay as they are.
- The 5 old rules of V5 are not brought back; the 9 milestone-shape rules live in the check.
