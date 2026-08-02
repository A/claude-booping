# Verify the finished sprint

One guardrail pass over the sprint, run once at sprint end. Report pass/fail and stop there:
apply no fixes, edit no code, pass no judgement on code quality or architecture. A red result is
evidence handed back to the runner, not work to start.

Your run-time context names the attached repo, the sprint branch (already checked out, every
milestone committed) and the plan — `plans/{slug}/index.md`.

## Commands to run

Run the plan's **Final Verification** commands verbatim as authored, then the project's own
lint / typecheck / formatter / test commands. Once, over the finished sprint.

Discover the project's commands in this order, stopping at the first that answers:

1. the repo's `CLAUDE.md`
2. the project-local `_booping/skill_develop.md`
3. inspection of the repo — `package.json` scripts, `pyproject.toml` / `ruff.toml` / pyright
   config, `Justfile` / `Makefile` targets, `.eslintrc`, `tsconfig.json`, `cargo.toml`
   dev-dependencies

Run only the configured-but-manual tools. Hook-enforced ones — `.pre-commit-config.yaml`,
`.husky/`, `lefthook.yml`, `.git/hooks/`, a blocking CI gate — already fired when the milestones
were committed; skip them and report each skip so the coverage stays auditable. The two buckets
are [development_quality_checks.md](${CLAUDE_PLUGIN_ROOT}/docs/development_quality_checks.md)'s
split; its per-milestone framing does not apply here — the suite runs once, at sprint end.

If the project has no configured quality tooling at all, say so and fall back to the plan's Final
Verification alone.

## Plan bookkeeping

Read the plan off disk and check what the loop actually wrote, not what it reported: every task
DoD checkbox `[x]`, every milestone status `done`. Each is its own check.

## Artifact

None. Write nothing — no fixes, no plan edits, no report file. The block you return is the whole
artifact.

## Return format

```markdown
- `<command>`[ (plan Final Verification)] — PASS|FAIL — <evidence>
- skipped: <tool or config file> — hook-enforced, fired at commit time
- plan: DoD checkboxes — PASS|FAIL — <n of m [x], else the unticked ones by task>
- plan: milestone statuses — PASS|FAIL — <all done, else the milestones still open>
- verdict: green|red — <n> of <m> commands passing|failing, <n> of 2 plan checks passing|failing

```