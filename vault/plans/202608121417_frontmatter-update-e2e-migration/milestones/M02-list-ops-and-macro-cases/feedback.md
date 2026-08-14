**Blocked (1/2)**: sprint verify red — all 14 M02 txtar cases fail in a clean `just ci` / `uv run pytest e2e -k frontmatter` run: append-identical-twice-idempotent, append-only-nothing-to-change-exits-1, append-to-absent-key, append-to-existing-list, append-to-null-key, append-to-scalar-exits-1, combined-operations, malformed-jinja-exits-2, real-macro-execution, remove-key, stubbed-macro-date-like-value-stays-string, stubbed-macro-string-value, stubbed-macro-with-args, unknown-macro-exits-2.

What was checked: `just ci` stops at the e2e stage with 14 failed / 55 passed; the same 14 reproduce with `cd booping-python && uv run pytest e2e -k frontmatter -q`.

What was wrong: the committed expected blocks in those cases do not match what the CLI actually emits — divergences include a missing blank line after the frontmatter closing `---`, quoted-string style differences, and error-message wording. The expected sections were not produced by the mandated rebaseline procedure (`uv run pytest e2e --txtar-update -k frontmatter` from `booping-python/`), or were edited after it.

What the next attempt must do:
- From `booping-python/`, run `uv run pytest e2e --txtar-update -k frontmatter` to rewrite the expected blocks of the failing cases from real CLI output, then read each rewritten case and confirm the recorded contract is the intended behavior (per the M01/M02 authoring procedure).
- If a case's fixtures or cmd are themselves wrong (not just the expected blocks), fix the fixtures/cmd first, then rebaseline.
- Confirm green without the flag: `uv run pytest e2e -k frontmatter -q`, then `just ci` from the repo root.
- Land as a new commit on `bench/z-ai-glm-4-5-air`; never amend.
