# Verify the plan's external references

The input carries the decomposed plan the user confirmed at the decomposition gate, together with
the run slug and the run workdir. Settle every external thing the plan names — versions, tags,
endpoints, flags, options — against the vendor's own documentation read now, correct what is
wrong directly in the plan, and record the check. A milestone is executed in a fresh session from
the plan alone: a pin that was retired or a flag that was renamed fails there, so it is caught
here, before the user approves.

The step always runs and always writes its file. A plan naming nothing external is answered with a
`Nothing to check` verdict, never with an absent artifact.

## What counts as an external reference

Anything the plan names that is owned outside this repository and can drift: package and library
names with their versions, container image tags, API endpoints and the payload shapes read from
them, third-party CLI commands and their flags, framework or tool config options and their
defaults, and the normative requirements of a standard the plan leans on.

The repository's own surfaces are not references: repo paths, module and symbol names, the
project's own `just` / make targets, its internal APIs and settings names. Do not list them as
rows, and do not report them as unverifiable.

Sweep the whole plan, not just the task table — a reference reachable only through a DoD line, a
milestone `Verify` command, the Architecture prose or the Decisions list is still a reference, and
the same literal appearing in several places is one row.

One row per external thing, not per mention and not per field of it. An endpoint, a client library
or a document the plan reads is one reference carrying the surface the plan uses off it: the keys
and calls it names — the metadata field, the response attribute, the exception it catches — are
settled inside that row's `Plan claims` and `Upstream` cells, never split into rows of their own.
A dependency is one reference whether its pin appears in the manifest, a DoD line and a `Verify`
command; a CLI command and the flag the plan passes it are one reference.
Two independent things are two rows even when a single document settles both; one thing stays one
row even when settling it takes several documents — the row's `Upstream` cell says what each of
them establishes, and `Source` carries the document that backs the verdict.

## Check against the source, now

- Open the upstream source for each reference in this run: the package registry page, the vendor's
  documentation, the release notes or changelog, the standard's own text. Recalling a version is
  not a check.
- Say what that source says about that exact literal — the release that is current, that the tag is
  no longer published, the section that requires the pairing. "Still supported" backs nothing.
- Cite the source that carries the claim, with the date you retrieved it. A row whose URL does not
  cover its claim is worse than no row.
- When retrieval is unavailable — no search tool, a denied permission, a fetch that fails — the
  check still runs and the file still carries verdicts. Settle each reference against the canonical
  primary document for it (the package's registry page, the vendor's own reference, the standard's
  own text), cite that document by its stable URL, put the run date in `Source`, and correct in
  place every literal that document contradicts — a retired pin and an unpublished image tag are
  corrected on this path exactly as on the live one. Say in the **return block's** `## Notes:` —
  never in the artifact, whose sections are fixed — that the rows were not retrieved live this run,
  so the correction is re-checked before the plan is approved. A denied tool is never a blanket
  `unverifiable` verdict.
- No authoritative source covers it — the behaviour is convention, or every source is second-hand
  — the verdict is `unverifiable`: leave the plan exactly as written, name why nothing settles it,
  and never invent a source or a speculative fix. That verdict is for a reference no primary
  document settles, never for one this run merely could not open.
- A literal the source confirms current is `ok`. Do not downgrade a reference to manufacture a
  finding; a pass with nothing to correct is a result.

## Correct the plan in place

Every correction is a literal replacement in the plan file the input names, applied at **every**
occurrence — task body, DoD line, `Verify` command, prose alike. The surrounding text is not
rewritten.

The replacement keeps the form the plan wrote. An exact pin is replaced by another exact pin at a
concrete release — `pkg==1.2.3`, never widened to `pkg>=1.0,<2`, a comparator, an extra marker or
an unpinned name; a tag is replaced by a tag, a path by a path, a flag by a flag. Quoting,
spacing and the rest of the line stay exactly as the plan wrote them, so the swapped literal is
the only difference on that line.

What is folded in is the identity of the external thing — the version, the tag, the endpoint path,
the flag, the option name. How the plan *uses* that thing is not: a call the DoD names, the way a
response is read, the exception it catches, the payload key it expects are the task's own writing,
and a release that changes them is reported under the rule below, never edited into the DoD.

Nothing else in the plan is touched: no task or DoD rewording, no milestone added, split or
resequenced, no story point changed at task, milestone or sprint level, no frontmatter write. The
plan appears in the return only when at least one correction was made; a clean pass leaves the
file byte-identical.

When a correction reaches further than the literal — the current release renames the API a DoD
depends on, or plausibly changes what a task costs — that is reported, not resolved. Fold in the
literal, then write the invalidation into the return block's `## Notes:` for the approval summary.
Reopening a design call or an estimate is the user's move, taken at `present`.

## The artifact

Write `references.md` into the run workdir the input names — created on every path, never omitted.
Report it under the workdir-relative path the input gave, e.g. `_runs/groom/{slug}/references.md`;
mark the entry `[UPDATED]` instead of `[CREATED]` when a re-entered run finds the file already
there. No frontmatter — nothing stamps this file.

The H1 is `# references — {slug}`, carrying the run slug the input names.

`## Verdict` comes first on every path: one line carrying `Verified`, `Corrected` or `Nothing to
check`, an em dash, then the counts — how many references were checked, how many corrected, and
how many were unverifiable when any were. The counts match the rows below.

```
Corrected — 6 references checked, 2 corrected, 1 unverifiable.
```

On the **nothing-to-check** path the file ends at the verdict — no table, no further section — and
the verdict names the grounds rather than listing the repo's own paths and commands:

```
Nothing to check — 0 references checked. Every reference the plan makes is repo-internal: module
paths, the project's own `just` targets, and no dependency, image, endpoint or external flag.
```

Otherwise two sections follow, and two more appear only when they have entries:

- `## Checked` — a table whose columns are exactly `Reference`, `Named in`, `Plan claims`,
  `Upstream`, `Verdict`, `Source`. One row per reference. `Named in` points at the place in the
  plan — the milestone and the task, DoD or `Verify` command that names it. `Plan claims` is the
  literal as the plan writes it. `Upstream` is what the source says about that literal. `Verdict`
  is `ok`, `corrected` or `unverifiable`. `Source` carries the `https://` URL and the `yyyymmdd`
  date it was retrieved — as `Source (checked 20260731)` in the header when one date covers every
  row, otherwise per cell; an `unverifiable` row is the only one that may carry `—`.
- `## Corrections` — one entry per `corrected` row, present only when there is one: the reference,
  the plan section it sits in, the `before → after` literals, why the old value is wrong, and the
  source with its checked date.
- `## Unverifiable` — one entry per `unverifiable` row, present only when there is one: what could
  not be settled, why no authoritative source covers it, and that the plan is left as written and
  flagged for the approval summary.

The sections appear in that order and no other H2 is added. `Verdict`, `Checked`, `Corrections`
and `Unverifiable` are the file's whole vocabulary — in particular the file carries no `## Notes`
section: retrieval caveats, blockers and invalidations belong to the return block's `## Notes:`
alone, which is a different document from this one.

## Return format

The reply to the harness is the block alone — no prose around it, no section the format does not
name. The step never pauses the run and never asks the user anything: this block's `## Notes:` is
the only channel a caveat, a blocker or a request reaches the runner through, and `present` carries it to
the user.

```
## Changed:

- [UPDATED] plans/{slug}.md — 2 corrections folded in
- [CREATED] _runs/groom/{slug}/references.md — 6 checked, 2 corrected, 1 unverifiable

## Notes:

- corrected: `redis==5.0.1` → `redis==6.4.0` (M1) — the pinned line predates the timeout kwarg the task's Verify passes
- corrected: `redis:7.2-alpine3.18` → `redis:7.2-alpine` (M1) — the tagged image is no longer published
- unverifiable: `X-RateLimit-Reset` unit — convention only, no normative source; surface at present
```

On a clean pass the plan is absent from the list:

```
## Changed:

- [CREATED] _runs/groom/{slug}/references.md — 3 checked, 0 corrected

## Notes:

- plan untouched — every reference matches current upstream docs
```

`## Notes:` is written for the approval summary, not as a second copy of the Checked table: it
carries the corrections whose effect reaches the work, every unverifiable reference, and any
invalidation the user has to call.
