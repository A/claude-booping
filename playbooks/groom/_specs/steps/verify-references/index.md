---
status: done
reviewed_at: 20260731 19:52
fixtures_reviewed_at: 20260731 20:07
suite_reviewed_at: 20260731 20:34
---

[← index](../../index.md)

# verify-references

## Contract

- **Delegation** — assisted: the runner extracts the plan's references, decides which need
  checking, and owns the record and the plan corrections; the configured researcher agent checks
  the selected references against upstream docs and reports back. The runner records the agent's
  id in `index.md` so a loopback resumes the same agent instead of spawning a fresh one.
- **Needs** —
  - the external references the confirmed plan names — package and library versions, container
    image tags, API endpoints and their payload shapes, CLI commands and flags, config options
    and their defaults — each with the place in the plan that names it
  - `research.md`'s source table, when it exists — a reference it already backs with a dated
    URL is reused, not re-fetched
  - the current upstream documentation for what remains — the vendor's own docs, release notes,
    changelogs and package registries, read now rather than recalled
- **Value** — the plan an agent will execute names things that exist today. The check is sized
  to the risk: verified are the **novel, load-bearing** references — the pin that was chosen
  this run, the flag the design leans on, the endpoint recalled from memory; well-known stable
  syntax (POSIX and coreutils basics, a tool's decade-old flags) is not re-verified, and a
  reference `research.md` already dated is taken as checked. So a milestone does not fail in a
  fresh session on a pin that was retired or a flag that was renamed — without re-fetching the
  manual for `mktemp`. The step always runs and always writes its record: a plan naming nothing
  worth checking is answered with a `Nothing to check` verdict, never an absent record, so
  `present` never has to work out whether verification happened.
- **Output files** —
  - `[UPDATED] plans/{slug}/index.md` — the `## References` section: the verdict first
    (`Verified`, `Corrected` or `Nothing to check`, with the checked / corrected / unverifiable
    counts on one line), then `### Checked` — one table row per reference carrying where the
    plan names it, what the plan claimed, what upstream says, the verdict (`ok`, `corrected`,
    `unverifiable`, `skipped — stable` for what was deliberately not fetched) and the source URL
    with its retrieval date, then `### Corrections` — one entry per corrected reference with the
    plan section, the before → after literal, the reason and the source — and `### Unverifiable`
    when any reference had no authoritative source. The section is written on every path.
  - `[UPDATED] plans/{slug}/plan.md` — each correction folded in as a literal replacement
    wherever the wrong value appears: task bodies, DoD lines, Verify commands. Nothing else is
    touched — no milestone edits, no re-estimation, no frontmatter writes. The plan appears in
    `## Changed:` only when at least one correction was made; a clean pass leaves it untouched.
  - nothing else — a correction that invalidates a design call or a task's size is reported, not
    acted on
- **Step report** — `## Changed:` list, each entry annotated with its counts, plus `## Notes:`
  carrying every correction that changes the shape of the work and every unverifiable reference,
  so `present` can surface them in the approval summary.
- **Review gate** —
  - none — the step never pauses the run; corrections reach the user through `present`, where the
    approval summary carries them and a change request can send the run back
  - a correction that invalidates an architecture call or an estimate is never resolved here: it
    is written into `## Notes:` for the approval summary, and the loopback is the user's to take

## Example artifact

`plans/20260731-rate-limit-public-api/index.md`, the `## References` section:

```markdown
## References

Corrected — 6 references checked, 2 corrected, 1 unverifiable.

### Checked

| Reference | Named in | Plan claims | Upstream | Verdict | Source (checked 20260731) |
| --------- | -------- | ----------- | -------- | ------- | ------------------------- |
| `redis` (PyPI) | M1 · "add the cache dependency" | `redis==5.0.1` | `6.4.0` current; the 5.x line no longer gets fixes | corrected | https://pypi.org/project/redis/ |
| cache image tag | M1 · compose service | `redis:7.2-alpine3.18` | that tag is no longer published; `7.2-alpine` is | corrected | https://hub.docker.com/_/redis |
| `Retry-After` on 429 | M2 · "return 429 over quota" | required alongside 429 | RFC 6585 §4 defines exactly this pairing | ok | https://www.rfc-editor.org/rfc/rfc6585 |
| cache backend path | M1 · settings change | `django.core.cache.backends.redis.RedisCache` | built in since Django 4.0 | ok | https://docs.djangoproject.com/en/stable/topics/cache/ |
| `uv add --group dev` | M1 · Verify command | flag as written | current CLI accepts it | ok | https://docs.astral.sh/uv/reference/cli/ |
| `X-RateLimit-Reset` unit | M2 · response headers | epoch seconds | no normative source — the header family is convention | unverifiable | — |

### Corrections

- **`redis` pin** — M1, task "add the cache dependency": `redis==5.0.1` → `redis==6.4.0`. The
  pinned line is unmaintained and predates the connection-timeout kwarg the task's Verify command
  passes. https://pypi.org/project/redis/ (checked 20260731)
- **cache image tag** — M1, compose service `cache`: `redis:7.2-alpine3.18` → `redis:7.2-alpine`.
  The base-image-qualified tag was pulled from the registry; the unqualified tag tracks the same
  7.2 line. https://hub.docker.com/_/redis (checked 20260731)

### Unverifiable

- `X-RateLimit-Reset` unit (epoch seconds vs seconds remaining) — RFC 6585 standardises `429` and
  `Retry-After` only; the `X-RateLimit-*` family is convention and implementations differ. Left
  as the plan states it and flagged for the approval summary.
```

The plan edit is a literal replacement in place — the surrounding task text is not rewritten:

```markdown
- **M1.2** Add the cache dependency — `uv add --group dev redis==6.4.0`, compose service `cache`
  on `redis:7.2-alpine`.
  - DoD: `uv run python -c "import redis"` succeeds against the compose service.
  - Verify: `docker compose up -d cache && uv run pytest tests/test_cache.py -q`
```

## Return Format

```markdown
## Changed:

- [UPDATED] plans/20260731-rate-limit-public-api/plan.md — 2 corrections folded in
- [UPDATED] plans/20260731-rate-limit-public-api/index.md — references: 6 checked, 2 corrected, 1 unverifiable

## Notes:

- corrected: `redis==5.0.1` → `redis==6.4.0` (M1) — the pinned line predates the timeout kwarg the task's Verify passes
- corrected: `redis:7.2-alpine3.18` → `redis:7.2-alpine` (M1) — the tagged image is no longer published
- unverifiable: `X-RateLimit-Reset` unit — convention only, no normative source; surface at present
```

On a clean pass the plan is absent from the list:

```markdown
## Changed:

- [UPDATED] plans/20260731-fix-stale-session-cookie/index.md — references: 3 checked, 0 corrected

## Notes:

- plan untouched — every reference matches current upstream docs
```
