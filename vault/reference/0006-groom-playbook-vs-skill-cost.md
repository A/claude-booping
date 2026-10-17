---
type: reference
title: Groom cost — playbook versus the old skill
summary: On one measured request the playbook groom took 2.4× the wall time, 5.2× the main-thread API calls and 3.0× the output tokens of the old /groom skill.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: live
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/evals groom.md
---

## Facts

- Note dated 2026-08-02 (file date). The request groomed, the model and whether both
  runs used the same request are not named in the source.
- Wall time (span): 9m 13s old `/groom` vs 21m 53s playbook groom (2.4×); active time
  5m 53s vs 16m 11s (2.75×); user wait 3m 20s vs 5m 42s.
- Main-thread API calls: 20 vs 104 (5.2×). Output tokens (main): 47,621 vs 144,317
  (3.0×). Cache reads 1.32M vs 10.24M (7.7×); cache writes 186k vs 573k (3.1×). Final
  context ~88k vs ~161k (1.8×).
- Tool calls: 8 (3 Read, 2 AskUserQuestion, 1 Write, 1 Bash, 1 Agent) vs 45 (21 Edit,
  15 Bash, 4 Write, 3 Read, 2 Agent).
- Researcher agents: 1 (63k tokens, 60s, 11 tools) vs 2 (89k + 66k tokens, 137s + 113s,
  29 + 29 tools); agent time ~1m vs ~4m 10s.
- User interaction: 2 AskUserQuestion and no typed replies vs no AskUserQuestion and 2
  typed prose replies.

## How to check

- [clarify] The source names no recipe; `booping session-stats` on the two groom
  sessions gives the token figures.
