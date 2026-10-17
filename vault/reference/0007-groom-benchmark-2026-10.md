---
type: reference
title: Groom benchmark 2026-10 — variants, rule ablation, plan split
summary: What the October 2026 groom benchmark measured, what the model does without being told, what it cost and where the data lives.
created_by: claude
created_at: 2026-10-16
updated_at: 2026-10-17
status: live
sources: [vault/adr/0030-groom-drafts-the-whole-plan-in-one-pass.md, vault/adr/0031-a-script-cuts-the-plan-into-milestone-files.md]
---

## Facts

- Data: GitLab `lab/booping-benchmarks`, branch `feat/groom-bench`, directory `groom/` — corpus
  (`corpus/<task>/task.yaml`, `incidents.yaml`), runs (`results/r1`, `results/r2`, `results/r2-redo`),
  judges (`results/*/judge*`), `ablation/report.md`, `split/report.md`, `xreview/`. Client feed inputs
  are not in git.
- Corpus: six past tasks (s1, s2 small; m1, m2 medium; c1, c2 complex), plus routing cases s3 (a small
  decided request sent to develop without a groom) and m3 (a medium request groomed by the old groom).
- Judging: free judges with no rubric and no final solution (codex, a neutral `claude -p`, Gemini 3.1
  Pro through pi with code access); a mechanical incidents metric — share of what really went wrong
  that a plan would have prevented (major ×2, minor ×1); c1's incidents are not plan-preventable.
- Variants, round 2 (12 plans per task on s1, m2, c1): staged draft V3 6.7 and V3a 6.6 mean judge
  score, template-only V2 5.8, V3 plus five old groom rules V5 5.3; the old multi-step groom V0 took
  13–23 min and $4.25–5.62 a plan against V3a's 7.9 min and $2.75. Only staged variants found m2's
  60 s gateway take cap. Spread inside one variant (V3: 9 and 4 on s1) exceeds the V3–V3a gap.
- Rule ablation (45 rules of V3 in 9 batches, 40 runs, s1 and s2): 16 rules the model follows without
  being told, 16 carried by the template's sections, 9 milestone-shape rules it misses even when told
  (36–58%), 4 weak; removing a batch does not change the cost per plan ($2.16–2.73 against $2.33).
- Telling the model more can hurt: V5's five extra rules made it the fastest and the worst variant
  and it never found the m2 defect.
- Plan split (12 single-file plans): a script cutting on headings passes every threshold on 12/12 at $0;
  Sonnet rewriting 12/12 at $0.71; Haiku mapping line ranges 8/12; Haiku rewriting 6/12.
- Review as a separate step (`groom/xreview`, 36 plans, Opus fold-in, judged on readiness and on
  challenging the request): a fresh Opus "double-check" helps (readiness +1.77 / +1.22, challenge
  +2.27 / +1.42, codex / claude-p) and beats V3's in-session self-review head to head, at +10.4 min a
  plan; the cross-review prompt on Opus, codex and Gemini show no measurable effect; no reviewer found
  m2's 60 s cap. Decision: adr/0035 (no review step).
- Cost of the Claude runs recorded in `result.json`: variants $145 (61 runs), ablation $97 (40),
  split $16 (48) — about $257 and 302 M tokens, mostly cache reads; codex and Gemini judges, the
  `claude -p` judges and the implementation runs are not in that sum.

## How to check

- `jq -s '[.[] | .total_cost_usd // 0] | add' $(find groom -name result.json)` in the benchmark repo.
- `groom/ablation/rule_table.md` and `groom/split/report.md` hold the per-rule and per-plan numbers.
