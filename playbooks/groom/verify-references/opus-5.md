# Verify the plan's external references

This step is yours: you select which references are worth checking, you fold the corrections into
the plan and you write the record. The upstream reading is not — delegate it to
`{{ config.research_agent }}` and let only the checked rows come back, so the documentation never
enters your context.

A milestone is executed in a fresh session from `plans/{slug}/plan.md` alone: a pin that was
retired or a flag that was renamed fails there, so it is caught here, before the user approves. The
step always runs and always writes its section — a plan naming nothing worth checking is answered
with a `Nothing to check` verdict, never with an absent record.

## What counts as an external reference

Anything the plan names that is owned outside this repository and can drift: package and library
names with their versions, container image tags, API endpoints and the payload shapes read from
them, third-party CLI commands and their flags, framework or tool config options and their
defaults, and the normative requirements of a standard the plan leans on.

The repository's own surfaces are not references: repo paths, module and symbol names, the
project's own `just` / make targets, its internal APIs and settings names. Do not list them as
rows, and do not report them as unverifiable.

Sweep the whole plan, not just the task table — a reference reachable only through a DoD line, a
milestone `Verify` command, the Architecture prose or the Decisions list is still a reference.

One row per external thing, not per mention and not per field of it. An endpoint, a client library
or a document the plan reads is one reference carrying the surface the plan uses off it: the keys
and calls it names — the metadata field, the response attribute, the exception it catches — are
settled inside that row's `Plan claims` and `Upstream` cells, never split into rows of their own. A
dependency is one reference whether its pin appears in the manifest, a DoD line and a `Verify`
command; a CLI command and the flag the plan passes it are one reference. Two independent things
are two rows even when a single document settles both; one thing stays one row even when settling
it takes several documents.

## Select what is actually checked

The check is sized to the risk. What goes to the agent is the **novel, load-bearing** references —
the pin chosen this run, the flag the design leans on, the endpoint recalled from memory, anything
a milestone fails on if it is wrong. Two classes never go:

- **Well-known stable syntax** — POSIX and coreutils basics, a tool's decade-old flags, a
  standard's long-settled requirement. Fetching the manual for `mktemp` buys nothing. Row it
  `skipped — stable` with the reason, and cite no source.
- **Already dated by `research.md`** — when that file exists, a reference its `## Sources` table
  backs with a URL and a retrieval date is taken as checked. Reuse that row: verdict `ok`, and the
  source cell carries `research.md`'s URL and its date. Do not re-fetch it.

Both classes are rowed, never dropped — `present` reads what was checked and what was deliberately
not.

## Delegate the reading

Spawn `{{ config.research_agent }}` with the selected references — each with the literal the plan
writes, where the plan names it, and what the plan claims of it — and this return contract:

- one row per reference and nothing else: the reference, the plan's claim, what upstream says about
  that exact literal, the verdict (`ok`, `corrected`, `unverifiable`), and the source URL with its
  `yyyymmdd` retrieval date
- upstream read now, from the primary source — the package registry page, the vendor's own
  reference, the release notes, the standard's own text. Recalling a version is not a check, and a
  claim it cannot cite is dropped rather than softened
- no page dumps, no quoted documentation, no prose around the rows

Say what the source says about that exact literal — the release that is current, that the tag is no
longer published, the section that requires the pairing. "Still supported" backs nothing; a row
whose URL does not cover its claim is worse than no row.

`unverifiable` is for a reference no primary document settles — the behaviour is convention, or
every source is second-hand. It is never the verdict for a reference the run merely could not open:
when retrieval is unavailable, each reference is still settled against the canonical primary
document, cited by its stable URL, and every literal that document contradicts is corrected in
place exactly as on the live path. Say in the return block's `## Notes:` — never in the section —
that the rows were not retrieved live this run, so the correction is re-checked before approval.

A literal the source confirms current is `ok`. Do not downgrade a reference to manufacture a
finding; a pass with nothing to correct is a result.

## Correct the plan in place

Every correction is a literal replacement in `plans/{slug}/plan.md`, applied at **every**
occurrence — task body, DoD line, `Verify` command, prose alike. The surrounding text is not
rewritten.

The replacement keeps the form the plan wrote. An exact pin is replaced by another exact pin at a
concrete release — `pkg==1.2.3`, never widened to `pkg>=1.0,<2`, a comparator, an extra marker or
an unpinned name; a tag is replaced by a tag, a path by a path, a flag by a flag. Quoting, spacing
and the rest of the line stay exactly as the plan wrote them, so the swapped literal is the only
difference on that line.

What is folded in is the identity of the external thing — the version, the tag, the endpoint path,
the flag, the option name. How the plan *uses* that thing is not: a call the DoD names, the way a
response is read, the exception it catches, the payload key it expects are the task's own writing,
and a release that changes them is reported under the rule below, never edited into the DoD.

Nothing else in the plan is touched: no task or DoD rewording, no milestone added, split or
resequenced, no story point changed at task, milestone or sprint level, no frontmatter write. The
plan appears in the return only when at least one correction was made; a clean pass leaves the file
byte-identical.

When a correction reaches further than the literal — the current release renames the API a DoD
depends on, or plausibly changes what a task costs — that is reported, not resolved. Fold in the
literal, then write the invalidation into the return block's `## Notes:` for the approval summary.
Reopening a design call or an estimate is the user's move, taken at `present`.

## The section to write

`## References` in `plans/{slug}/index.md` — the only thing this step writes besides the plan.
Preserve the file's frontmatter and the sections other steps own; the section is written on every
path, and on a re-entry it is revised in place rather than having a second round appended to it.

The section opens with its **verdict line**: one line carrying `Verified`, `Corrected` or `Nothing
to check`, an em dash, then the counts — how many references were checked, how many corrected, and
how many were unverifiable when any were. The counts match the rows below.

```
Corrected — 6 references checked, 2 corrected, 1 unverifiable.
```

On the **nothing-to-check** path the section ends at the verdict — no table, no H3 — and the
verdict names the grounds rather than listing the repo's own paths and commands:

```
Nothing to check — 0 references checked. Every reference the plan makes is repo-internal: module
paths, the project's own `just` targets, and no dependency, image, endpoint or external flag.
```

Otherwise one H3 follows, and two more appear only when they have entries:

- `### Checked` — a table whose columns are exactly `Reference`, `Named in`, `Plan claims`,
  `Upstream`, `Verdict`, `Source`. One row per reference. `Named in` points at the place in the
  plan — the milestone and the task, DoD or `Verify` command that names it. `Plan claims` is the
  literal as the plan writes it. `Upstream` is what the source says about that literal, or, on a
  skipped row, why it needed no fetch. `Verdict` is `ok`, `corrected`, `unverifiable` or
  `skipped — stable`. `Source` carries the `https://` URL and the `yyyymmdd` date it was retrieved
  — as `Source (checked 20260731)` in the header when one date covers every row, otherwise per
  cell; an `unverifiable` or `skipped — stable` row is the only one that may carry `—`.
- `### Corrections` — one entry per `corrected` row, present only when there is one: the reference,
  the plan section it sits in, the `before → after` literals, why the old value is wrong, and the
  source with its checked date.
- `### Unverifiable` — one entry per `unverifiable` row, present only when there is one: what could
  not be settled, why no authoritative source covers it, and that the plan is left as written and
  flagged for the approval summary.

The H3s appear in that order and no other is added — in particular the section carries no notes
subsection: retrieval caveats, blockers and invalidations belong to the return block's `## Notes:`
alone.

## Return format

The step never pauses the run and never asks the user anything: the return block's `## Notes:` is
the only channel a caveat, a blocker or an invalidation reaches the runner through, and `present`
carries it to the user.

```
## Changed:

- [UPDATED] plans/{slug}/plan.md — 2 corrections folded in
- [UPDATED] plans/{slug}/index.md — references: 6 checked, 2 corrected, 1 unverifiable

## Notes:

- corrected: `redis==5.0.1` → `redis==6.4.0` (M1) — the pinned line predates the timeout kwarg the task's Verify passes
- corrected: `redis:7.2-alpine3.18` → `redis:7.2-alpine` (M1) — the tagged image is no longer published
- unverifiable: `X-RateLimit-Reset` unit — convention only, no normative source; surface at present
```

On a clean pass the plan is absent from the list:

```
## Changed:

- [UPDATED] plans/{slug}/index.md — references: 3 checked, 0 corrected

## Notes:

- plan untouched — every reference matches current upstream docs
```

`## Notes:` is written for the approval summary, not as a second copy of the Checked table: it
carries the corrections whose effect reaches the work, every unverifiable reference, and any
invalidation the user has to call. The reply is these two sections alone: no prose before the first
heading, nothing outside them, and no `(none)` placeholder in an empty section.
