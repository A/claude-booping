# Frame the request

The input carries the user's request verbatim, the run's start time, the task-type catalogue with
its per-type grooming guidance, the project's own conventions, and the plans already filed in the
vault — parked ones included. On a re-run it also carries the framing the previous pass wrote and
the user's answers to the scope questions it returned.

Settle the whole run's framing before a single research token is spent: one restated problem, one
task type, boundaries decidable on sight, and the scope-challenge questions the user must answer.
Read what the framing needs off disk first — the conventions, the guidance for the type you land
on, the filed plans — and write nothing before you have.

## The slug

One slug names the run: `yyyymmdd-hh-mm_{kebab-title}`, minted from the run start time and a short
title you give the work. Both files below share that stem. Two cases keep an existing slug: a
re-run keeps the first pass's, and a run that adopts a parked plan takes that plan's filename stem
— no fresh slug is minted.

## Duplicate work

Read the filed plans before framing anything. When one already covers the request, it is adopted,
never re-created:

- the user names it — adopt it: the slug is that plan's filename stem, and the framing you write
  is that plan's work as the request restates it. One plan's framing, not a second plan's.
- the user does not name it but restates its work — resolve the overlap before you frame. Adopt
  the parked plan the same way, or, when the overlap is partial and only the user can call it,
  ask. Either way its path appears in your return. Never mint a second plan for parked work.

## The files to write

`_runs/groom/{slug}/intake.md` — the framing document:

- frontmatter: `reviewed_at: null`, and nothing else. The confirm edge stamps it.
- `# Intake — {title}`, then exactly these H2s, in this order:
  - `## Request` — the request as a blockquote, character-for-character. Nothing added, nothing
    tidied, nothing summarised.
  - `## Restated problem` — what the system does today and what must change, in the request's own
    domain terms. Carry no requirement the request does not carry.
  - `## Task type` — one backticked type from the catalogue, with the rationale that rules each
    sibling type out by name and on a stated test.
  - `## Scope boundaries` — a bold **In scope** group and a bold **Out of scope** group, both
    non-empty, every item decidable on sight. Out of scope names the adjacent work the request
    could plausibly be read to include — the neighbouring surfaces, not strawmen.
  - `## Scope challenge` — `- [ ]` items, at least one, always. Each challenges what the request
    pulls in that it does not state — new components, dependencies, APIs, workflow changes — is
    answerable in one line, and asks nothing the request already answers.
- nothing else. No blast radius, no file list, no architecture call, no milestone, no estimate:
  every one of those belongs to a later step and is wrong here.

`plans/{slug}.md` — the plan file, identity only:

- frontmatter: `title` and `type` from the framing, `status: in-spec`, `created` the run's date as
  `YYYY-MM-DD`, `sp: null`, `summary: ""`, and every remaining key of the project's plan
  frontmatter shape at `null`.
- no body — nothing but whitespace after the closing `---`. The body is a later step's to write.
- adopting a parked plan: edit that file in place. Flip its `status:` to `in-spec` and refresh
  `title` and `type` to match the framing; leave `created` and every other existing value
  untouched. Never rename it, never add a second file.

On a re-run, rewrite `intake.md` alone. Fold each answer in where it belongs — a boundary an
answer moved now sits under the group it moved to — and mark every question it settles `- [x]`
with the answer on the line, so no box is left open. Leave what the answers did not touch exactly
as it was, the request blockquote included. Touch the plan file only if an answer moved the title
or the type.

## Return format

```
## Changed:

- [CREATED|UPDATED] _runs/groom/{slug}/intake.md
- [CREATED|UPDATED] plans/{slug}.md

## Notes:

- task type: {type}
- plan: `plans/{slug}.md` ({created|adopted|unchanged})
- {n} scope question(s) open

## Questions:

1. {one-line-answerable scope question}
```

A first pass always returns at least one question — challenging scope is unconditional. On the
re-run whose answers settle the framing, `## Changed:` carries `intake.md` alone, `## Notes:`
reports what the answers changed, and `## Questions:` comes back empty.
