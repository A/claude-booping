---
type: reference
title: "Postmortem: mechanisms built without a reader"
summary: Between 2026-10-15 and 2026-10-18 booping grew a config key and three journal CLIs that nothing needed; removed on 2026-10-18, with the rule wording and the ADR guide that let them in.
created_by: claude
created_at: 2026-10-18
updated_at: 2026-10-18
status: live
tags: [postmortem]
---

## Facts

- 2026-10-15: one owner request was cut into sibling plans groomed the same afternoon — corrections
  log (202610151532), autonomy modes (202610151609), then the project manager. Each built its own
  mechanism: `booping correction add|list` with a transcript lookup proving the quote verbatim and a
  dialogue link; `core.autonomy` with an invalid-value STOP, a project-context line and a render branch;
  `booping defaults add`; `booping items ask|answer` with a two-part answered test. About 550 lines and
  35 e2e cases.
- `core.autonomy` never decided anything `booping run --autonomous` did not: a supervised project's
  child run already got the supervised text plus the autonomous preamble, and the preamble won.
- adr/0026 weighed "log as it happens" against "mine transcripts at retro"; adr/0027 weighed "mode per
  project" against "one fixed mode". Neither weighed prose, an existing primitive or building nothing.
  An audit of all ADRs the same day scored 6 of 32 as checkbox alternatives (0016, 0017, 0019, 0026,
  0027, and the first draft of 0037) and 18 as missing one cheap option; every 1 introduced a
  mechanism, and authorship did not matter — the owner's one mechanism ADR scored 1 too.
- 2026-10-18 the owner asked why `core.autonomy` was not a boolean, then why it existed, then what
  `correction add` bought over the model writing the file. The agent first reconstructed reasons for
  both designs, then reversed within the hour. adr/0036 moved autonomy to prose; adr/0037 replaced the
  three CLIs with vault files over `scaffold`, `frontmatter-update` and `query`, after a generic
  `booping journal` was built and discarded the same day.
- Probes the same day (reference/0009): the old wording of value/0015 and rule/0025 ("whatever can be
  computed runs as code") scored worst of all variants, below no rule at all, and moved a prose task
  into a validated transition payload; a fresh model given a sibling's plan generalised that plan's new
  CLI, and given the items alone or together it built none.

**Causes:**

- Code had no bar to clear. rule/0030 asks a prompt instruction for a measured miss; rule/0025 sent to
  code whatever *could* be computed, with no reader asked for. A value pulling toward code had no
  counterweight, so a plan citing value/0015 never had a departure to flag — the same gap
  reference/0008 found: values justified how a mechanism was built, never whether it should exist.
- A mechanism justified itself: the config key was read by the template branch made for it.
- The ADR guide asked for a real alternative but named none of the cheap ones, and its "'leave it as it
  is' … is no option" read as leave to drop building nothing; `rows: {min: 2}` passes "new vs old".
- Siblings of one class were groomed in parallel, each blind to the other; when one sees the other's
  plan, it anchors on it.
- The agent defended existing code by reconstruction before testing what it bought.

**Remedies:**

- rule/0025 rewritten: who reads the result decides prose or code, readers counted only when they
  exist or are asked for, prose when unsure; value/0015 rewritten to match. Wording chosen by probe.
- `src/specs/README.md`: a decision that adds a mechanism weighs prose, an existing primitive and
  building nothing, each as a row or with one line saying why it does not apply.
- booping:rule/0035: the manager grooms same-class items together or in sequence with the earlier
  plan linked, never in parallel.
- Agent memory: on "why is X so", records first, then "what do we lose without X".
- OI-0006: run the loss test over every booping subcommand.

## How to check

- adr/0026, adr/0036, adr/0037; `git show 3db6f75:vault/adr/0027-autonomy-modes.md`; commit 2597086.
- Plans `vault/plans/202610151532_corrections-log/`, `vault/plans/202610151609_autonomy-modes/`.
- reference/0009 and its raw data in `~/.tmp/booping-probes-2026-10-18/`.
