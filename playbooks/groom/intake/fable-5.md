# Frame the request

Settle the whole run's framing before a single research token is spent: one restated problem, one
task type, boundaries decidable on sight, the scope-challenge questions the user must answer, and
the web-research decision. Read what the framing needs off disk first — the project's own
conventions, the per-type guidance for the type you land on, the plans already filed in the vault
— and write nothing before you have.

## Duplicate work

Read the filed plans, parked ones included, before framing anything. When one already covers the
request it is adopted, never re-created:

- the user names it — adopt it, and the framing you write is that plan's work as the request
  restates it. One plan's framing, not a second plan's.
- the user does not name it but restates its work — resolve the overlap before you frame. Adopt
  the parked plan the same way, or, when the overlap is partial and only the user can call it,
  ask. Either way its path appears in your return.

Adoption fixes the run slug: it is the parked stub's filename stem, so `plans/{slug}/` is the run
workdir from that point on. Never mint a second plan for parked work.

## The files to write

Two files in the plan directory, and nothing else. No blast radius, no file list, no architecture
call, no milestone, no estimate: every one of those belongs to a later step and is wrong here.

`index.md` — the run's artifact. Its frontmatter was bootstrapped by the first transition and the
run's hooks own it: preserve it byte for byte. Under the H1, write the `## Framing` section with
exactly these H3s, in this order:

- `### Request` — the request as a blockquote, character-for-character. Nothing added, nothing
  tidied, nothing summarised.
- `### Restated problem` — what the system does today and what must change, in the request's own
  domain terms. Carry no requirement the request does not carry.
- `### Task type` — one backticked type from the catalogue, with the rationale that rules each
  sibling type out by name and on a stated test.
- `### Scope boundaries` — a bold **In scope** group and a bold **Out of scope** group, both
  non-empty, every item decidable on sight. Out of scope names the adjacent work the request could
  plausibly be read to include — the neighbouring surfaces, not strawmen.
- `### Web research` — one line, `Requested` or `Not requested`, with what settles it: the user
  asked for deep web research in the request itself or explicitly → `Requested`; anything else →
  `Not requested`. Write the line on both paths; `research-web` executes it mechanically and no
  later step re-judges it.
- `### Scope challenge` — `- [ ]` items, at least one, always. Each challenges what the request
  pulls in that it does not state — new components, dependencies, APIs, workflow changes — is
  answerable in one line, and asks nothing the request already answers.

`plan.md` — identity only:

- frontmatter: `title` and `type` from the framing, `status: in-spec`, `created` the run's date as
  `YYYY-MM-DD`, `sp: null`, `summary: ""`, and every remaining key of the project's plan
  frontmatter shape at `null`.
- no body — nothing but whitespace after the closing `---`. The body is `draft-plan`'s to write.

## Adopting a parked plan into the directory

In this order, and only this order:

1. create `plans/{slug}/`, the stub's filename stem as the slug
2. write `plans/{slug}/plan.md` from the stub's content — its frontmatter with `status:` flipped
   from `backlog` to `in-spec` and `title` and `type` refreshed to match the framing, `created`
   and every other existing value untouched, its body carried over as it is
3. delete the stub file `plans/{slug}.md`

Re-entry is tolerant: directory present and stub gone → the adoption is done, leave it alone; both
present → finish by deleting the stub. No path ends with both on disk.

## Re-run

Rewrite the `## Framing` section alone. Fold each answer in where it belongs — a boundary an
answer moved now sits under the group it moved to — and mark every question it settles `- [x]`
with the answer on the line, so no box is left open. Leave what the answers did not touch exactly
as it was, the request blockquote included. Touch `plan.md` only if an answer moved the title or
the type.

## Return format

```
## Changed:

- [UPDATED] plans/{slug}/index.md — framing
- [CREATED|UPDATED] plans/{slug}/plan.md

## Notes:

- task type: {type}
- plan: `plans/{slug}/plan.md` ({created|adopted|unchanged})
- web research: {requested|not requested}
- {n} scope question(s) open

## Questions:

1. {one-line-answerable scope question}
```

A first pass always returns at least one question — challenging scope is unconditional. On the
re-run whose answers settle the framing, `## Changed:` carries `index.md` alone, `## Notes:`
reports what the answers changed, and `## Questions:` comes back empty.
