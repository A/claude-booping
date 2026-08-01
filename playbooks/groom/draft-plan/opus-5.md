# Write the plan

You hold the settled design — the `## Design` section of `index.md`: the chosen architecture and
why it won, the surface changes, the alternatives rejected, the trade-off calls the user made, and
the risks with their mitigations; the confirmed framing — the `## Framing` section, with the
restated problem, the task type, the scope boundaries and the user's answers to the scope-challenge
questions; the blast radius — the `## Blast radius` section, with the prior art and conventions
already in play; the plan-template catalogue, each entry with its name, its description and the
location to read its `# Plan Body` and `# Quality Checklist` from; the plan frontmatter shape; the
sizing scale and how many consecutive milestones one development briefing bundles; and whether the
project configures a cross-review agent, and which agent it names.

Turn the settled design into the executable plan. Decide no architecture here — it was settled
upstream and confirmed by the user; your judgment goes into decomposition, sizing, and fidelity to
what the design and the blast radius actually say.

## Choose the template

- Pick the catalogue entry whose name and description match the **dominant surface** of the work —
  the surface most of the milestones land on. A near miss loses on that surface, not on taste.
- Read the chosen file before drafting. The plan is written against its `# Plan Body` and verified
  against its `# Quality Checklist`; neither can be guessed from the catalogue line.
- When no entry fits, author one in the project's own `plan_templates/` first, then draft against
  it. The new template carries frontmatter `name` and `description` plus both `# Plan Body` and
  `# Quality Checklist` top-level sections, and is generic for its surface class: placeholders
  throughout, no path, milestone or story-point value from this run baked in. Never draft into a
  bad-fit template, never improvise a shape and name a template after it.

## Write the body

- The template's sections, section for section, in its order — none dropped, none extra. The only
  addition is `## Risk register` under the rule below.
- The narrative sections restate the design's settled calls in the plan's own voice: the placement,
  the wiring, the policies, the calls the user made. Add no architecture call the design does not
  carry, and drop none it does.
- Every path in a `Files` cell is one the blast radius names. No invented path, and no glob
  standing in for a file the map left unnamed.
- Each milestone heading carries its own total and state — `### M1: {name} — {N} SP | pending` —
  and the milestone holds a one-sentence `**Goal**`, a `**Verify**`, a task table with the columns
  `Task | Description | Files | SP | Status`, and one `#### Task N.M DoD` checkbox block per table
  row.
- `**Verify**` is a runnable invocation of the project's own tooling or a stated observable
  outcome. Every DoD checkbox names something observable — an invocation, an output, an exit code,
  an asserted behaviour. "Works correctly" is not one, and neither is a TBD.
- Each milestone is executable in a fresh session with only the plan file as context: no "as
  above", nothing that depends on state an earlier milestone's agent held. Size them against how
  many consecutive milestones one briefing bundles.
- The out-of-scope section mirrors the framing's exclusions, and no milestone or task targets them.

## Size honestly

Story points go on every task, sum into each milestone's total, and sum into the sprint total.

The estimate is the honest one for the work as it stands. Never shave a task to land under the
re-decompose threshold, never pre-split one, never inflate one. Enforcing that threshold and
flagging a split belong to the sizing pass that runs after you — claim neither in the plan nor in
the return.

## Frontmatter

- `sp` — the sprint total. `summary` — one line of plain plan intent, ≤ ~120 characters, phrased as
  the visible outcome, not the engineering output.
- `title` and `type` are intake's. Correct them only where the design changed them; the H1 matches
  `title` and is the only H1 in the file.
- `status` is never written here, and neither are the date and outcome keys — the run machine's
  edge hooks own them. Every key intake left `null` stays `null`.

## Verify against the checklist

Before the cross-review, walk the chosen template's `# Quality Checklist` item by item against the
artifact as written. An unsatisfied item is fixed, not reported as satisfied, and an anti-pattern
item holds only when the anti-pattern is absent in fact.

## Cross-review

The input says whether the project configures a cross-review agent and, when it does, names it.

**No agent configured** — nothing is spawned, the plan is returned as drafted, and the drafting
gate is vacuously satisfied. Nothing reviewer-flavoured goes into the plan: no findings list, no
severity vocabulary, no "per review" hedge. There was no review.

**An agent configured** — after the checklist pass and before returning, hand the finished draft to
it exactly once, spawned through the Agent tool with `subagent_type` set to the name the input
gives. This is the run's only cross-validation pass; the external-validator path booping's
cross-validation doc describes is never called from a playbook run.

Its return contract is fixed here and never renegotiated mid-run. Brief it for findings only, one
per line:

```
- CRITICAL|RISK|NOTE: {finding} — {plan section}
```

or the literal `no findings`, and nothing else — no preamble, no verdict line, no summary.

Then dispose of every finding:

- `CRITICAL` — folded into the plan, or recorded as a deferral.
- `RISK` — folded in when it does not reopen a call the user already settled; otherwise recorded.
- `NOTE` — folded in at your discretion, and it never blocks.
- A finding that reopens a settled design call is acted on **nowhere** in the plan: not as a task,
  not as a DoD item, not as a hedge in the architecture section, not as a deferral dressed up as
  agreement. It travels as a note line so the runner can route it back to design, and the rest of
  the review is disposed on its own merits — the routed finding never stalls the plan and never
  becomes a question.

Deferred findings are recorded in `## Risk register`, one line each: the finding, its severity, and
the reason it was deferred. Deferred findings are all it holds — the design's own risks are never
copied into it. They restate in the narrative sections whose calls they qualify, beside the
mitigations the design gives them. When the chosen template defines no such section, add it directly
after the out-of-scope section; when nothing was deferred and the template defines none, the plan
carries no risk register at all.

## The artifact

`plans/{slug}/plan.md` — the plan file intake created. Report it `[UPDATED]`, never `[CREATED]`: it
exists from wave 1 and is never renamed or re-created. It is the only file you write, apart from a
plan template you had to author. `index.md` gets nothing from this step — the cross-review outcome
travels in the return, not in a section or a file of its own.

## Return format

```
## Changed:

- [UPDATED] plans/{slug}/plan.md — template `{name}`, {N} SP

## Notes:

- milestones: M1 {name} {N} SP, M2 {name} {N} SP; sprint total {N} SP
- quality checklist (`{name}`): all items pass
- cross-review (`{agent}`): 3 findings — 1 CRITICAL folded in (the fail-open path was untested,
  now a task DoD item), 1 RISK deferred to the risk register (a caller outside the run's scope
  keeps the old surface), 1 NOTE folded in
```

With no cross-review agent configured the last note is one line instead:

```
- cross-review: no `cross_review` agent configured — not run
```

A template you had to author is listed `[CREATED]` above the plan entry. A finding routed back to
design is one more `## Notes:` line naming the finding, the settled call it reopens, and that it
was not folded in. The reply to the harness is these two sections alone: no prose before the first
heading, nothing outside them, and no `(none)` placeholder in an empty section.
