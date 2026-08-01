# Settle the architecture

You hold the confirmed framing — the restated problem, the task type, the scope boundaries and the
user's answers to the scope-challenge questions; the `## Blast radius` section of `index.md` with
its prior art and the conventions in play; and `research.md` when the user asked for web research,
or the framing's line saying they did not. On a loopback you also hold the user's objection and
the design call it targets, and a `## Design` section already exists.

Settle the architecture **with the user, in this conversation**. The calls that are yours you
decide; the calls that are theirs you ask, and the step does not end while one is unanswered.
There is no confirm status after this step — the conversation is the alignment.

## How to decide

- Argue the approach against what the blast radius actually names — the files, modules and
  surfaces it mapped, the prior art it found, the conventions it says are in play. Never name a
  path, module, dependency or convention the inputs did not.
- Every unknown the blast radius left for design is decided in `### Approach`, or surfaced as a
  trade-off or a risk. None is dropped silently.
- The approaches `research.md` gathered and you did not take belong in `### Alternatives`, each
  with the single reason it lost. Every pitfall it names is either designed against in
  `### Approach` / `### Surface changes` or carried into `### Risks` with its mitigation.
- No research requested means no external practice was gathered: argue from the blast radius and
  the prior art alone. Claim no current practice, compare no libraries, assert no version, and
  carry no URL, source table or retrieval date into the file.
- Surface changes are implementable from as written: field and key names, endpoint shapes, config
  keys and their defaults, CLI flags, concrete paths. "Config will change" is not a surface change.

## Ask the calls that are the user's

- A call is theirs when its consequence is — policy, cost, blast radius, what breaks for whom.
  Implementation choices are yours to settle in `### Approach`; a design that hands them over is
  unfinished. When the work carries no such call, say so in one line rather than manufacturing one.
- Ask the open calls together as numbered questions, each with its options, the consequence of
  each, your recommendation, and the part of the plan that cannot be written until it is answered.
- Record each answered call under `### Trade-offs` with the option taken and why. Nothing is
  parked there unanswered.
- An objection that needs blast radius or external practice the research pass missed — or a
  mid-design request for web research — sends the run back to research rather than into another
  design pass. Say so and stop; do not guess the missing ground.

## The section to write

`## Design` in `index.md` — the only thing this step writes. `plan.md` keeps its identity
frontmatter and stays untouched until the plan is drafted. Preserve the file's frontmatter and the
sections other steps own; write these H3s, in this order, none extra:

- `### Approach` — the chosen architecture and pattern choice with the rationale that made it win,
  named against the modules and files the blast radius identified
- `### Surface changes` — every data, API, config and CLI change the approach implies, each
  concrete enough to implement from
- `### Alternatives` — each approach considered and not taken, with the one reason it lost
- `### Trade-offs` — the calls that were the user's, each with the option taken and why
- `### Risks` — what can go wrong on this approach, each with its mitigation

On a loopback re-entry the section is revised in place, never appended to: settled subsections
stay as they are, only the reopened call and whatever depends on it is rewritten, and the option
the objection displaces moves into `### Alternatives` with the reason it lost. Add no round,
revision or changelog subsection.

## Return format

```
## Changed:
- [UPDATED] plans/{slug}/index.md — design

## Questions:
1. The first open trade-off call, asked as a question, with its options, your recommendation and
   the part of the plan that cannot be written until it is answered.
```

One numbered question per call still open — no extra, none missing — and the section comes back
empty once every call is answered and the run moves to drafting. The reply is these two sections
alone: no prose before the first heading, nothing outside them, and no `(none)` placeholder in an
empty section.
