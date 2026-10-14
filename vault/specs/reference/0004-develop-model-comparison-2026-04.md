---
type: reference
title: Develop model comparison, April 2026
summary: One develop diff each from Claude Opus 4.7, Minimax 2.7 and GLM 5.1 scored 9.7, 7.2 and 6.4 of 10; only Opus produced a correct, plan-compliant diff.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: live
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/develop-comparation.md
---

## Facts

- Note dated 2026-04-29 (file date). The task, the plan, who or what graded, and how
  many runs per model are not named in the source.
- Claude Opus 4.7 — 9.7/10 overall: plan adherence 10, correctness and edge cases 10,
  code quality 9.5, testing 10, performance and safety 9. Verdict: clean, compliant with
  the architecture, handles edge cases.
- Minimax 2.7 — 7.2/10 overall: plan adherence 7, correctness 8, code quality 5,
  testing 7, performance and safety 9. Verdict: fixes the context-dropping bug but with
  severe DRY violations and algorithmic logic inside Jinja2 templates.
- GLM 5.1 — 6.4/10 overall: plan adherence 9, correctness 4, code quality 6, testing 8,
  performance and safety 5. Verdict: fails to pass context into nested partials, which
  breaks the pipeline and adds heavy I/O.
