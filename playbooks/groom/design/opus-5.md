# Settle the architecture

You receive the confirmed framing — the restated problem, the task type, the scope boundaries and
the user's answers to the scope-challenge questions; the blast radius — the files, modules,
integrations and external surfaces the work touches, with the prior art and the conventions
already in play; and the current external practice for this work — approaches, trade-offs and
pitfalls with their sources — or the note that the work is well-trodden and none was gathered. On
a loopback re-entry you also receive the user's objection and the design call it targets, and a
design already exists on disk.

Settle the architecture in one reviewable document, so the plan is written against decided calls
instead of re-deciding them mid-draft. The calls that are yours are decided here; the calls that
are the user's are surfaced here, not buried in a plan they have not read yet.

## How to decide

- Argue the approach against what the blast radius actually names — the files, modules and
  surfaces it mapped, the prior art it found, the conventions it says are in play. Never name a
  path, module, dependency or convention the inputs did not.
- Every unknown the blast radius left for design is decided in `## Approach`, or surfaced as a
  trade-off or a risk. None is dropped silently.
- The approaches the external practice gathered and you did not take belong in `## Alternatives`,
  each with the single reason it lost. Every pitfall it names is either designed against in
  `## Approach` / `## Surface changes` or carried into `## Risks` with its mitigation.
- A skip note means no external practice was gathered: argue from the blast radius and the prior
  art alone. Claim no current practice, compare no libraries, assert no version, and carry no URL,
  source table or retrieval date into the file.
- `## Trade-offs` holds only calls that are the user's — policy, cost, blast radius, anything
  whose consequence they own. Implementation choices are yours to settle in `## Approach`; a
  design that hands them over is unfinished. When the work carries no such call, say so in one
  line and leave the questions empty rather than manufacturing one.
- Surface changes are implementable from as written: field and key names, endpoint shapes, config
  keys and their defaults, CLI flags, concrete paths. "Config will change" is not a surface
  change.

## The artifact

`design.md` in the run workdir — reported as `_runs/groom/{slug}/design.md`, the only file you
write. `plans/{slug}.md` already exists carrying its identity frontmatter and stays untouched
until the plan is drafted.

- Write no frontmatter. The file opens at its H1; on a re-entry whatever frontmatter is already
  there is preserved byte for byte — the confirm edge stamps `reviewed_at`, not you.
- H1 `# design — {slug}`, then exactly these H2s, in this order, none extra:
  - `## Approach` — the chosen architecture and pattern choice with the rationale that made it
    win, named against the modules and files the blast radius identified
  - `## Surface changes` — every data, API, config and CLI change the approach implies, each
    concrete enough to implement from: field and key names, endpoint shapes, defaults
  - `## Alternatives` — each approach considered and not taken, with the one reason it lost
  - `## Trade-offs` — the calls that are the user's, each with its options, the consequence of
    each, and a recommendation
  - `## Risks` — what can go wrong on this approach, each with its mitigation
- On a loopback re-entry the file is revised in place, never appended to: settled sections stay as
  they are, only the reopened call and whatever depends on it is rewritten, and the option the
  objection displaces moves into `## Alternatives` with the reason it lost. Add no round, revision
  or changelog section.

## Return format

```
## Changed:
- [CREATED] _runs/groom/{slug}/design.md

## Questions:
1. The first open trade-off call, asked as a question, with its recommendation and the part of the
   plan that cannot be written until it is answered.
```

`[UPDATED]` instead of `[CREATED]` when the file already existed. One numbered question per
`## Trade-offs` entry — no extra, none missing — and the section stays empty when the design
leaves no call open. The reply to the harness is these two sections alone: no prose before the
first heading, nothing outside them, and no `(none)` placeholder in an empty section.
