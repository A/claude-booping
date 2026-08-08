For each **accepted issue** from the triage at `gather-feedback`, do focused root-cause work:

1. **Code reading** — read the related files referenced by the trigger or the user's refinement. No broad scans; only the files specifically implicated. When the issue involves convention or pattern mismatches, also read the project `CLAUDE.md` and compare against what the code actually does — a stale or incomplete `CLAUDE.md` is a common root cause for convention drift.
2. **Web research** — `WebSearch` for current best practices for the underlying class of problem; `WebFetch` to pull a specific doc when a search result needs verification. For wide research that must aggregate across many sources, delegate per the agent roster above.
3. **Prevention options** — synthesize concrete, process-level moves that would have headed this off. Examples of the right shape: an extra planning step ("when env vars change, include a CI-config task in the plan"), a specific edge case to anticipate up-front, a user notification to surface at the right moment ("communicate which env vars need to be added in GitHub before merge"), a developer-workflow tweak ("run the formatter after every change"). For accepted issues tagged as ignored-lesson or plan-stage lesson gap, also review whether the lesson itself needs to change — sharper wording, a clearer trigger, a different placement (planning vs execution), or whether the process around enforcing it failed (lesson exists but never reached the right phase).

Each item ends with three deliverables in context, ready for `synthesize`:

- **Root cause** — what the underlying issue actually is (one to three sentences).
- **Prevention options** — one or more concrete moves that would have surfaced or prevented this.
- **Optional follow-up** — concrete next step the user might take, if any.

### Lesson gaps

Loaded lessons (from `~/Claude/{project}/lessons/` or project `CLAUDE.md` instructions) that should have prevented or caught one or more flagged problems but were not applied. For each:

- `lessons/XXXX_lesson-title.md` — rule was "...", but we did "..." instead, which caused [which issue(s)].
