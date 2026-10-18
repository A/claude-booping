---
type: adr
title: Groom drafts the whole plan in one staged pass
summary: Groom is the plan template plus research then draft (V3a), no self-review step, without the 16 rules the model follows unprompted; the draft is one file.
created_by: claude
created_at: 2026-10-16
updated_at: 2026-10-17
status: accepted
values: [value/0012, value/0002, value/0010]
issues: []
sources: [vault/idea/0003-groom-depth-scales-with-task.md]
---

## Context

A benchmark in `booping-benchmarks/groom` (idea/0003) ran variants on six past tasks in
isolated environments; round 2 judged 12 plans per task (V2, V3, V3a, V5 × 3) on s1 (small), m2
(medium) and c1 (complex) with codex and a neutral `claude -p`, no rubric and no final solution,
plus a mechanical incidents metric (what a plan would have prevented of what really went wrong).
Each variant writes the whole plan as one file.

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
template's sections, and 9 milestone-shape rules it misses even when told (36–58%); removing a
batch does not change the cost per plan.

## Criteria

- Plan quality at least that of V3 on the benchmark tasks.
- Cost and wall time well under V0's.

## Decision

Groom is one drafting pass on the plan template with two stages, research then draft, and no
separate self-review step (V3a). The 16 rules the ablation shows the model follows unprompted and the
anti-pattern list leave the prompt; the template's sections stay. The draft is the whole plan in
one file, milestones included; how it becomes milestone files is adr/0031. The 9 milestone-shape
rules the model misses even when told are not repeated in the prompt either: they are checked after
the split (adr/0031).

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [V3a: research then draft](#v3a-research-then-draft) | accepted | medium | high | Quality of V3 at less cost and time |
| [V3 with self-review](#v3-with-self-review) | rejected | medium | high | +0.1 points for +12% cost and +15% time |
| [V3 with the old groom's rules](#v3-with-the-old-grooms-rules) | rejected | low | high | Last of the four on judges and incidents |

### V3a: research then draft

The template plus a research stage over the code and a drafting stage, in one session.

- **Pros:** quality on par with V3; about 2× faster and 1.7× cheaper than V0; the shortest prompt.
- **Cons:** judged on three tasks with n = 3 per variant; spread inside a variant is large.
- **Complexity:** medium — the groom playbook is rewritten around one drafting step.
- **Reversibility:** high — the old playbook stays in git.

### V3 with self-review

The same drafting pass with a self-review stage at the end.

- **Pros:** highest mean score, best incidents on m2.
- **Cons:** the gain over V3a is inside the noise; the step costs money and time on every plan.
- **Complexity:** medium.
- **Reversibility:** high.

### V3 with the old groom's rules

V3 plus five rules from the current groom the one-shot variants had missed (scoped Verify, a section
shape before improvising, self-contained milestones, assumption lines, a short summary).

- **Pros:** names what reviewers asked for before.
- **Cons:** last of the four on both judges and incidents; never found m2's defect; the run is the
  fastest, which suggests the rules pull effort from research into form.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- `playbooks/groom` is rewritten around one drafting step; its snapshot reports change.
- The plan template states the one-file milestone format adr/0031 cuts on.
- A light path for small, already-decided requests is a follow-up (idea/0009, corpus case
  `s3-booping-specs-site-registries`).
