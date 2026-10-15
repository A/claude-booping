# M09 feedback

**Blocked (1/2)**: DoD 9.2 `lesson` grep over `vault/specs` still hits records that state targeted lessons as the current carrier; the vault docs playbook report still names the old story and `_lessons/`.

The first attempt's edits (CLAUDE.md, docs/, opus-5.md, story/0004 rename, glossary, rule/0018, rule/0020, adr/0001, specs/README.md, idea/0002) are in the working tree, checked and kept — build on them, do not redo them. `just specs-check` is green.

What the next attempt must do (rule/0007 — stale references are cleaned in the same sprint):

1. Reword every sentence in `vault/specs` that presents targeted lessons as how booping works **now** into targeted rules (rule records with `targets:` + `brief:`), keeping each record's meaning; bump `updated_at: 2026-10-15` on each edited record; change no `targets:` line. Known hits:
   - `story/0007-external-agents.md` (summary, l18) — shaped per project by targeted rules; note `agent:` targets reach booping's own agents only, an external agent is shaped by a rule on the step that delegates (see `documentation/playbook.md` `## Rules` warning).
   - `story/0019-learn.md` (summary, l18, l23) — learn routes to a rule record in the project specs tier or a `CLAUDE.md` entry.
   - `adr/0012-driver-owns-the-vault.md` — summary and the `## Decision` lines (l27–34: "a targeted lesson (`agent:{id}`)" → targeted rule). Leave `## Context` and `## Alternatives` prose (l17, l49–57) as the history they record.
   - `adr/0014-external-tools-wire-in-through-config.md` — summary, `## Decision` (l32) and the accepted option's Cons (l52).
   - `idea/0007-guided-agent-wiring.md` (summary, l25) — the proposal produces a targeted rule.
   - `reference/0001-audience.md` (l29, l31), `reference/0003-documentation-surfaces.md` (l19) — "lessons" in the list of what advanced users author → "rules".
   - `adr/0003-render-at-skill-load.md` (l23, l46, l58) — "lessons" in the list of per-project context the render sees → "rules".
2. Leave as is (history or plain English, allowed by the DoD): `value/0001` ("a lesson becomes a rule"), `value/0012`, `adr/0001` context/alternatives, `adr/0008` (migration 002 name), `adr/0011` alternative's Cons, `story/0015` l23 (what migration 002 did), `idea/0005` ("retro and lessons"), `reference/0005` (a dated bench finding), and the migration-004 link lines in rule/0010, 0012, 0015.
3. `vault/_playbooks/docs/_reports/output.md`: update exactly three lines to match a fresh `bin/booping render-playbook docs` — the two `Targeted lessons` feature-index rows (l204, l337) and the `documentation/vault.md` row (l399). Keep the `Date & time` line as committed; touch nothing else in the file.

Re-run: `rg -n -i 'lesson' vault/specs`, `rg -n 'targeted-lessons' . --glob '!vault/plans/**' --glob '!vault/retrospectives/**' --glob '!vault/codereviews/**'` (must print nothing), `just specs-check`.
