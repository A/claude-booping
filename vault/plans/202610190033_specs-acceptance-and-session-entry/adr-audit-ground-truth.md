# ADR alternatives audit — ground truth (2026-10-18)

An Opus subagent scored every ADR of this repo's project tier on the text alone, in the session that produced `src/specs/README.md:47`. Copied here from the session's task output, which lives under /tmp and does not survive.

## Rubric (verbatim)

For each ADR score 0–3:

- 3: the alternatives include the cheapest credible option(s) (prose/prompt, an existing primitive extended or generalised, or doing nothing — whichever apply) and each gets honest pros; the decision would survive a skeptic.
- 2: real alternatives, but one obvious cheap option is missing.
- 1: the alternatives are a straw man / a restatement ("one fixed mode", "what we do today") — the table exists to satisfy the schema.
- 0: no real choice was weighed (the record is really a rule, or the alternative is absurd).

## Scores

Scored against the tree at commit `2597086` plus that session's uncommitted vault edits. ADRs changed since (`git diff --stat 2597086 -- vault/adr`) or deleted (0005, 0012, 0013, 0023, 0027, 0028) are left out of a measurement.

| ADR | score | missing alternative (short) |
|---|---|---|
| 0001 | 2 | ship format + checker only; global tier as a shared dir |
| 0002 | 2 | a skill keeping resume state in frontmatter |
| 0003 | 3 | — |
| 0004 | 2 | warn only on unknown `core.*` keys |
| 0006 | 2 | shared status names as a convention |
| 0007 | 3 | — |
| 0008 | 2 | a query over retro/review artefacts instead of back-link keys |
| 0009 | 3 | — (measured) |
| 0010 | 2 | per-milestone status as a list in index.md |
| 0011 | 2 | no field: the body says in prose when to delegate |
| 0014 | 2 | the user's CLAUDE.md or a rule names the agent |
| 0015 | 2 | zero gates: the user interrupts in chat |
| 0016 | 1 | no review step, or a prose double-check line |
| 0017 | 1 | migration notes applied by hand or by an agent in prose |
| 0018 | 3 | — |
| 0019 | 1 | build nothing: `gh`/`glab` in prose |
| 0020 | 2 | delete the noisy tests, build no harness |
| 0021 | 2 | no suites: snapshots plus manual runs |
| 0022 | 2 | no cap, one briefing per wave |
| 0024 | 2 | no playbook: guide + CLI in plain chat |
| 0025 | 2 | one list file, or tracker issues |
| 0026 | 1 | a prose step grepping transcripts; do nothing |
| 0029 | 2 | a hand-kept index page; Obsidian |
| 0030 | 3 | — (benchmarked) |
| 0031 | 2 | don't split: develop reads sections by heading |
| 0032 | 2 | make the existing affordance visible; Obsidian |
| 0033 | 3 | — |
| 0034 | 2 | do nothing (rule briefs + the specs playbook) |
| 0035 | 3 | — |
| 0036 | 3 | — |
| 0037 | 1 | prose files by a `docs/` format, no CLI; delete and replace with nothing |

Distribution: 3 → 8, 2 → 18, 1 → 6 (incl. deleted 0027), 0 → none.
