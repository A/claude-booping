## Request

> groom this. And also {vault}/plans/{slug} - slug can be partially applied with `YYYYMMDDHHmm-` prefix. And need to decide what model must get back from scaffold call, to avoid double-checking created file. Mb this per file?
>
> ```
> ---
> [CREATED|UPDATED]: {path}
>
> {diff}
> ---
> ```

"groom this" carries the preceding conversation: seed the plan's `index.md` through `booping scaffold` instead of having the model transcribe a frontmatter block from the prompt.

## Task type

`feature` — new capability on existing surfaces: groom gains a scaffold-seeded plan creation path, `scaffold` gains a per-file receipt contract callers consume instead of re-reading files.

- Not `bug` — the `commit: null` gap at develop's intake is real, but it comes from a key with no producer, not a producer misbehaving. Fixed by adding the seed, not repairing an existing path.
- Not `refactoring` — observable surface changes: `scaffold` prints a different report, plan frontmatter carries values it never carried at creation, the groom prompt loses a block. No no-behaviour-change DoD is writable.

## Problem

`groom/intake` shows the model a literal frontmatter block (`_partials/plan_frontmatter.md`) and tells it to create `index.md` in that shape. Every value is transcribed by the model, `created` included.

1. **`commit:` has no producer at creation.** Stamped only by develop's `ready-for-dev → in-progress` hook, which fires at `provision` — after `develop/intake`, which reads it as its drift baseline and runs `git diff --name-only {plan.commit}..HEAD`. First sprint interpolates `null`. The check works only on re-entry, then against the previous sprint's start rather than what the plan was designed against.
2. **The shape lives in prose.** Included twice — intake, and via `plan_structure.md` at draft-plan — as a literal in the prompt. Nothing validates that what the model wrote matches it.
3. **Transcription risk on compared values.** A 40-char SHA copied by a model and compared by equality fails silently: a truncated copy is never equal, `{plan.commit}..HEAD` still resolves, so drift is reported forever without an error.

The primitive exists. `booping scaffold` renders each file through `build_source_env`, which registers `macro` as a Jinja global — `macro('core.macros.git_commit')` and `core.macros.date` work inside a scaffold tree today. `setup` and `playbook-authoring` already create their artifacts this way; the plan track does not.

One sub-problem the request names stays in scope:

- **Return contract.** `scaffold` prints `created file {path}` / `overwrote file {path}` plus a count line. That says a file exists, not what is in it, so a caller reads it back — the exact context cost this change removes.

The other — applying the `YYYYMMDDHHmm` prefix to the plan directory for the model — was considered and dropped: the preamble already renders `Plan dir: plans/{YYYYMMDDHHmm}_{kebab-title}/`, so the model substitutes the kebab title and passes the whole path. No CLI flag, no config dest pattern.

## Clarifications and Decisions

- Seeding at creation is not the hand-editing the driving protocol forbids: `status: framing` is already seeded that way, and load-bearing — `playbook-transition` rejects any target but the initial status when the artifact carries none.
- `commit:` seeded at groom is framing-time HEAD, not designed-against HEAD. Fails safe: an earlier base over-reports drift, never under-reports, and develop's intake filters by plan-touched files first.
- develop's `ready-for-dev → in-progress` hook keeps re-stamping `commit:` to sprint start — code-review's diff base unchanged.
- `retro:` stays `null` in the seed — it is the retro queue predicate (`where: {retro: null}`).
- The frontmatter partial was already edited this session (`sp: null`, `related_to: null`, `code_reviews: []`, `goal` and `split_from` dropped). That edit is the starting point, not part of the work.
- The receipt is diff-shaped, not verb-plus-body: a created file is a diff against nothing, and the CREATED/UPDATED distinction is readable from the diff itself rather than carried as a separate header line. Exact shape settles at design alignment.
- Slug prefixing stays with the model — the render already supplies the prefix.
- Sprint scope is the core only: the groom seed tree, intake calling it, the frontmatter partial leaving the prompt, and scaffold's report. Explicitly out: develop/intake's missing `commit: null` branch and its equality comparison, the `goal:` key reconciliation, and converting setup / playbook-authoring to the new receipt.
- Consequence accepted: with develop/intake untouched, the seed makes `commit:` present on new plans only — plans created before this change keep the `null..HEAD` behaviour.
- No post-implementation reshape milestone.
