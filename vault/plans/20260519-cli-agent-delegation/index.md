---
title: External CLI Agent Delegation for /develop
type: feature
status: done
sp: 14
split_from: null
created: 2026-05-19 00:00
planned: 20260519 19:05
started: 20260519 19:30
completed: null
retro: null
goal: null
commit: f50809da7e7a095ce6ce40d405290f1ba9893cbf
summary: "type: cli agent config + booping run-agent subcommand delegating /develop implementation to an external CLI worker"
---

# External CLI Agent Delegation for /develop

## Context

Today `/develop`'s Phase 3 step 3 hard-delegates implementation to `booping-developer`, a native Claude Code subagent invoked via the `Agent` tool. The roster of available workers per skill lives in `src/config.yaml` under `skills.<name>.agents.<id>` and renders into the skill body via `_partials/_available_agents.j2`. `/learn` writes per-agent extensions to `~/Claude/{project}/_booping/agent_<id>.md`; these are inlined into native agent bodies at build/render time via `_partials/_extra_instructions.j2`.

Users want to swap (or augment) the built-in developer with an external CLI worker — concretely `pi --print "<prompt>"` from the `@mariozechner/pi-coding-agent` bundle — while keeping the existing extension channel so `/learn`-emitted guidance still reaches the worker.

After this plan, an `agents` entry carries a `type: agent | cli` discriminator. For `type: cli`, the entry specifies a `command` (literal shell command, no placeholder). A new `booping run-agent <id>` CLI subcommand reads the prompt from stdin, appends the matching `_booping/agent_<id>.md` extension if present, then exec's `<command> "<final-prompt>"` with the final prompt as the last positional arg. Native entries carry `internal: true`; a per-skill `disable_internal_agents: true` filter removes them from the rendered roster so a project can run on cli workers only.

Scope is limited to `/develop`. Groom, retro, code-review, chat keep their native-only `agents` blocks unchanged for now.

## Decisions

- **Schema location**: extend the existing `skills.<name>.agents.<id>` entry — keep one source of truth. **Why**: avoids parallel `delegates:` block; existing renderer/loader already walks this path; per-skill filtering stays uniform.
- **Discriminator**: add `type: agent | cli` (default `agent` when omitted). **Why**: discriminator at entry level lets one skill mix native and cli workers if needed; default-to-`agent` preserves all current entries verbatim.
- **CLI command shape**: `command:` is a **Jinja2 template** with a single variable `prompt` (the composed extension + briefing string). At resolution time `booping run-agent` shell-quotes `prompt` (`shlex.quote`) before substitution, renders the template, then `shlex.split` + `subprocess.run` (no `shell=True`). When `command` contains no `{{ prompt }}` placeholder, the quoted prompt is appended as the last positional arg (fallback for simple shapes like `pi --print`). **Why**: matches booping's Jinja-everywhere convention; lets users put the prompt anywhere in the command (stdin pipe via `sh -c`, mid-arg, etc.); pre-quoting at substitution + no-shell exec prevents injection while still allowing user-controlled redirects via explicit `sh -c '...'`.
- **Skill body never sees `command`**: `_available_agents.j2` renders only `booping run-agent <id>` for cli entries — never the underlying `command`. Skill prose calls into `booping run-agent`; the CLI resolves the configured command from merged config. **Why**: keeps skills agnostic to the cli tool; no cli-specific syntax leaks into rendered skill bodies; swapping the underlying command never re-renders the skill.
- **Briefing transport**: stdin into `booping run-agent`. **Why**: no shell-escaping for multi-line briefings; Bash tool can pipe via `<<EOF` or `< briefing.md`.
- **Final-prompt composition (cli)**: `booping run-agent` reads `~/Claude/{project}/_booping/agent_<id>.md` first, then briefing from stdin, joins them as `<extension>\n\n---\n\n<briefing>` and passes the joined string as the command's positional arg. Extension goes first (role / project context); briefing follows (this turn's task). When the extension file is absent, the joined string is just the briefing — no separator, no preamble. **Why**: preserves `/learn`'s existing emit path with zero changes to `/learn`; uses the same per-agent file naming native entries already use; extension-first mirrors system-prompt / user-message convention; one channel, two consumers.
- **Native-only invocation guard**: `booping run-agent <id>` hard-errors when the resolved entry has `internal: true` or `type: agent`. This is a **defensive safety net only** — under normal flow the rendered Available Agents table directs the orchestrator to the `Agent` tool for native entries, so the guard never fires. **Why keep it**: misuse (`booping run-agent booping-developer`) fails loud with a clear message instead of silently hanging or spawning the wrong tool.
- **Filter flag**: per-skill `disable_internal_agents: bool` (default `false`). When true, `_available_agents.j2` skips entries with `internal: true`. **Why**: project-level switch keeps the core config intact while letting a project run cli-only; per-skill keeps the door open for future per-skill differences without a global flag.
- **Multi-worker selection in /develop**: if the rendered roster has exactly one entry after filtering, use it; if multiple, AskUserQuestion at Phase 1 grouping. **Why**: avoids a new "primary developer" field; mirrors existing AskUserQuestion patterns in the skill.
- **Pydantic validation on `Agent` config entry**: typed model with `type` enum + `command` required when `type=cli`. **Why**: catches typos (`tipe:`, `comand:`) at config-load time; cheap once we already use Pydantic for `Context`.
- **Manual prose reshape**: final milestone is a pause-for-review on rendered `develop.md.j2` and `_available_agents.j2`. **Why**: schema + skill-body churn typically exposes IA issues only post-render; per-project saved guidance to encode reshape as final milestone.

## Architecture

```
project ~/Claude/{project}/config.yaml
   skills.develop.disable_internal_agents: true
   skills.develop.agents.pi-mesh: { type: cli, command: "...", good_for: [...] }
        │
        ▼ deep-merge in Context.assemble()
src/config.yaml
   skills.develop.agents.booping-developer: { internal: true, good_for: [...] }
   skills.develop.agents.booping-researcher: { internal: true, ... }
        │
        ▼ validated by Pydantic AgentConfig model
Context.config["skills"]["develop"]["agents"]  (typed shape)
        │
        ▼ rendered by _partials/_available_agents.j2
              (filters `internal: true` when disable_internal_agents is set;
               renders short "to run, execute booping run-agent <id>" line per
               cli entry — never the underlying command)
develop.md.j2 Phase 3 step 3 — Delegate to worker
   ├── type: agent → Agent tool, subagent_type=<id>
   └── type: cli   → Bash: `cat briefing.md | booping run-agent <id>`
                        │
                        ▼ booping-python: commands/run_agent.py
                            1. Resolve <id> from merged config; hard-error
                               if internal: true or type: agent.
                            2. Read stdin → briefing.
                            3. Read ~/Claude/{project}/_booping/agent_<id>.md
                               (if exists) → extension.
                            4. final_prompt = extension + "\n\n---\n\n" + briefing
                               (briefing-only when extension absent).
                            5. Render command as Jinja2 with prompt=shlex.quote(final_prompt).
                               If template has no {{ prompt }}, append quoted prompt as last arg.
                            6. subprocess.run(shlex.split(rendered_command), shell=False)
                               — stdout streams to parent; exit code propagates.
```

`_partials/_extra_instructions.j2` is untouched — native agents still inline their extension at render time; cli agents get it at invocation time via `booping run-agent`. One channel (`_booping/agent_<id>.md`), two consumers.

## Milestones

### M1: Config schema + Pydantic validation + loader filter — 3 SP | done

**Goal**: `src/config.yaml` carries `internal: true` on native entries; `Agent` config entries are validated by a typed Pydantic model; `Context.config` filters internal entries when `skills.<name>.disable_internal_agents: true`.

**Verify**: `just test` green; `bin/booping debug-context` shows native entries with `internal: true`; a fixture project config with `disable_internal_agents: true` drops them from the dumped context.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Mark all current `skills.<name>.agents.<id>` native entries with `internal: true` across `src/config.yaml` (develop, groom, retro, code-review, chat). | `src/config.yaml` | 1 | done |
| 1.2 | Add Pydantic `AgentConfig` model (fields: `type: Literal["agent","cli"] = "agent"`, `command: str \| None = None`, `internal: bool = False`, `good_for: list[str] = []`, `bad_for: list[str] = []`) with validator: `type == "cli"` ⇒ `command` non-empty. Add Pydantic `SkillConfig` wrapper with `disable_internal_agents: bool = False` and `agents: dict[str, AgentConfig] = {}`. Validate on `Context.assemble()` after deep-merge; raise on invalid shape. **Do not** filter `internal: true` entries inside `Context.assemble()` — the loader stores the raw validated config so `booping run-agent` can still resolve internal ids and hard-error on them; the `disable_internal_agents` filter is applied in the renderer at template render time (M3). | `booping-python/src/booping/context/config.py`, `booping-python/src/booping/context/__init__.py` | 2 | done |

#### Task 1.1 DoD

- [x] Every current `skills.*.agents.*` entry in `src/config.yaml` has `internal: true`.
- [x] `bin/booping debug-context` dumps show the new key on every native entry.

#### Task 1.2 DoD

- [x] `AgentConfig` and `SkillConfig` Pydantic models live in `booping-python/src/booping/context/config.py` (or a sibling module imported from it).
- [x] `Context.assemble()` validates `config["skills"]` after deep-merge; raises a clear error on a `type: cli` entry missing `command`.
- [x] When project config sets `skills.develop.disable_internal_agents: true`, the merged `config["skills"]["develop"]["agents"]` **still contains** all entries (loader does not filter); filtering happens later in the renderer (M3).
- [x] New tests cover: native entry validates, cli entry without `command` errors, cli entry with `command` validates, `disable_internal_agents: true` does **not** strip entries from the loaded config (filter belongs to the renderer).

---

### M2: `booping run-agent` CLI subcommand — 4 SP | done

**Goal**: `cat briefing.md | booping run-agent <id>` resolves the agent from merged config, appends the matching `_booping/agent_<id>.md` extension, exec's the configured `command` with the final prompt as the last positional arg, streams stdout/stderr to the caller, propagates exit code. Hard-errors on `internal: true` or `type: agent`.

**Verify**: `just test` green; integration test runs `booping run-agent <id>` with a fake `command: "cat"` and asserts the stdout equals briefing + extension; `booping run-agent <native-id>` exits non-zero with a clear message.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Implement `commands/run_agent.py` (add_parser + handler). Args: `<id>` positional; optional `--briefing-file PATH` (else read stdin — but error early if stdin is a TTY, see DoD). Behaviour: call `Context.assemble()` (raw validated config — no `disable_internal_agents` filtering at the loader level per M1); look up `config["skills"]` for any skill whose `agents` contains `<id>`; if entry is missing, `internal: true`, or `type != "cli"`, print clear stderr and exit 2. **Vault resolution**: read the extension from `<context.project.directory>/_booping/agent_<id>.md` (the vault path already resolved by `Project.load_cwd`); when `context.project` is `None`, skip extension lookup and proceed with briefing only. Build `final_prompt = extension + "\n\n---\n\n" + briefing` (briefing only, no separator, when extension absent or empty). **Command rendering**: render the entry's `command` as a Jinja2 template with one variable `prompt = shlex.quote(final_prompt)`. If the template body contains no `{{ prompt }}` substring, fall back to appending the quoted prompt as the last positional arg. Execute via `subprocess.run(shlex.split(rendered_command), check=False, shell=False)`; forward stdout/stderr; exit with the child's return code. | `booping-python/src/booping/commands/run_agent.py`, `booping-python/src/booping/cli.py` | 3 | done |
| 2.2 | Tests under `booping-python/tests/commands/run_agent_test.py` mirroring existing `render_test.py` pattern (subprocess against `bin/booping`, fixture vault under `booping-python/tests/__fixtures__/vault-with-cli-agent/`). Cases: agent-not-found exits 2; internal agent exits 2; type=agent exits 2; cli agent with no extension passes briefing only; cli agent with extension prepends extension + separator before briefing; stdin path and `--briefing-file` path both work; non-zero child exit propagates; TTY-stdin guard exits 2 with a clear message when stdin is a TTY and no `--briefing-file` is provided; `command` without `{{ prompt }}` placeholder appends prompt as last arg; `command` with `{{ prompt }}` substitutes at that position; prompt with shell metacharacters (`$VAR`, backticks, quotes, newlines) round-trips without injection. Use fixtures with both shapes: `command: "cat"` (no placeholder, appends) and `command: "sh -c 'printf %s {{ prompt }}' --"` (explicit placeholder via shell). | `booping-python/tests/commands/run_agent_test.py`, `booping-python/tests/__fixtures__/vault-with-cli-agent/` (new fixture: `config.yaml` + `_booping/agent_<id>.md`) | 1 | done |

#### Task 2.1 DoD

- [x] `bin/booping run-agent --help` lists the subcommand with the documented args.
- [x] Resolves agent id across all `skills.*.agents` (uniqueness across skills not enforced — first match wins; document this in `--help` or the source docstring).
- [x] Reads briefing from stdin when `--briefing-file` is absent. If `sys.stdin.isatty()` is true and `--briefing-file` is absent, exits 2 with a one-line stderr telling the caller to pipe input or pass `--briefing-file PATH` (prevents indefinite hang in interactive shells).
- [x] Extension path is `<context.project.directory>/_booping/agent_<id>.md`. When `context.project` is `None`, extension lookup is skipped. The file being absent never raises.
- [x] Hard-errors (exit 2 with one-line stderr) on missing id, `internal: true`, or `type: agent`.
- [x] Exit code of `booping run-agent` equals the exit code of the spawned `command`.
- [x] `command` is rendered as Jinja2 with `prompt = shlex.quote(final_prompt)` before exec. `subprocess.run(..., shell=False)` — no shell expansion of the substituted prompt at exec time.
- [x] When `command` template has no `{{ prompt }}` placeholder, the quoted prompt is appended as the last positional arg.

#### Task 2.2 DoD

- [x] Test file covers all bullets listed in task 2.2 description.
- [x] Tests use a temp vault fixture (mirrors the pattern used elsewhere in `booping-python/tests/`).
- [x] `just test` exits 0.

---

### M3: Template rendering — `_available_agents.j2` extension — 2 SP | done

**Goal**: `_partials/_available_agents.j2` skips `internal: true` entries when the skill's `disable_internal_agents` is true. Per-entry rendering branches on `type`:

- `type: agent` — render the existing native shape (name + good_for / bad_for) **plus** a short explicit invocation line: `Invoke via the \`Agent\` tool with \`subagent_type="<id>"\`.`
- `type: cli` — render the new cli shape: `This is a \`cli\` agent. To run it, execute: \`booping run-agent <id>\` (pipe the briefing on stdin).` No underlying `command` rendered.

`good_for` and `bad_for` blocks are each wrapped in `{% if ... %}` so missing/empty fields render nothing.

Existing native-only skills (groom, retro, code-review, chat) gain one new line per entry (the explicit `Agent`-tool invocation) — otherwise byte-identical.

**Verify**: `bin/booping render src/templates/skills/develop.md.j2` against a fixture config (a) with no overrides — native entries rendered with the new explicit invocation line — and (b) with a project config adding a `pi-mesh` cli entry + `disable_internal_agents: true` — only `pi-mesh` rendered, with the cli invocation line and no `command` block.

Rendered native entry shape (target output):

```markdown
### `booping-developer`

Invoke via the `Agent` tool with `subagent_type="booping-developer"`.

**Good for:**
- All coding tasks — always delegate; never edit application code from the orchestrator
```

Rendered cli entry shape (target output):

```markdown
### `pi-mesh`

This is a `cli` agent. To run it, execute: `booping run-agent pi-mesh` (pipe the briefing on stdin).

**Good for:**
- Concrete code change in a git-tracked project, expressible with testable acceptance

**Bad for:**
- Exploratory questions or dirty/non-git repos
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Extend the macro: (a) filter loop on `internal` flag when `disable_internal_agents` is set; (b) for `type: agent` entries (default) emit the explicit `Invoke via the \`Agent\` tool with \`subagent_type="<id>"\`.` line; (c) for `type: cli` entries emit the `This is a \`cli\` agent. To run it, execute: \`booping run-agent <id>\` (pipe the briefing on stdin).` line — no `command` block; (d) wrap `good_for` and `bad_for` blocks each in `{% if spec.good_for %}` / `{% if spec.bad_for %}`. **Apply the four-check IA pass** (Scoping, Duplication, Configurability, Hierarchy — see lesson `0004_information-architecture-pattern.md`) to the edited macro before saving: no residual negative rules, no duplicate prose with other partials, no hard-coded values that should be config, no detail level mismatch (the macro is a low-level renderer; long-form explanation belongs in `docs/cli_agent_delegation.md`). | `src/templates/_partials/_available_agents.j2` | 1 | done |
| 3.2 | Render-snapshot tests under `booping-python/tests/commands/available_agents_test.py`: (a) default config — rendered `develop` skill contains the explicit `Agent`-tool invocation line under each native entry; (b) cli override — with a project config adding a cli entry + `disable_internal_agents: true`, native entries are absent and the cli `### \`pi-mesh\`` block + "this is a `cli` agent... `booping run-agent pi-mesh`" line are present and the underlying `command` string is **not** present. | `booping-python/tests/commands/available_agents_test.py`, `booping-python/tests/__fixtures__/vault-with-cli-agent/` (reused from M2) | 1 | done |

#### Task 3.1 DoD

- [x] Macro filters `internal: true` entries iff `skills.<name>.disable_internal_agents` is true.
- [x] `type: agent` entries render the explicit `Invoke via the \`Agent\` tool with \`subagent_type="<id>"\`.` line.
- [x] `type: cli` entries render the short `booping run-agent <id>` line; no `command` text appears in the rendered output.
- [x] `good_for` / `bad_for` blocks each gated on a non-empty list.
- [x] Rendered output for groom/retro/code-review/chat diffs only by the new explicit `Agent`-tool invocation line under each entry (no other deltas).
- [x] Four-check IA pass run on the edited macro; pass notes recorded in the PR / sprint description.

#### Task 3.2 DoD

- [x] Tests assert: native default rendering matches baseline; cli override rendering shows cli entry + invocation line; `command` literal is absent from the rendered skill body.
- [x] `just test` exits 0.

---

### M4: `/develop` skill body — branch on agent type + multi-worker selection — 3 SP | done

**Goal**: `src/templates/skills/develop.md.j2` Phase 3 step 3 no longer hard-codes `booping-developer`. Worker selection: if the rendered roster has one entry, use it; if multiple, AskUserQuestion at Phase 1 (Plan groupings) to pick one for the sprint. Step 3 prose explicitly covers both invocation paths:

- `type: agent` (native) → `Agent` tool with `subagent_type=<id>`.
- `type: cli` → `Bash` tool, briefing piped to `booping run-agent <id>` on stdin. For long-running commands invoke with `run_in_background: true` and poll.

The skill body **never references the underlying `command`** — `booping run-agent` resolves it.

**Verify**: `bin/booping render src/templates/skills/develop.md.j2` produces a rendered body where Phase 3 step 3 references the table rather than naming `booping-developer`; AskUserQuestion clause appears in Phase 1.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Edit `develop.md.j2`: rewrite Phase 3 step 3 to branch on the selected worker's type (native → `Agent` tool with `subagent_type=<id>`; cli → `Bash` piping briefing to `booping run-agent <id>`); rewrite Phase 1 to include the worker-pick clause. Worker-pick wording: "If the rendered Available Agents table contains more than one entry, present them via `AskUserQuestion` and **hold the selected worker id in-session** — `/develop` is a single continuous session, no persistence to the plan file. Use the same worker id for every milestone group in this sprint." Note long-running cli commands may need `run_in_background` + polling — link to `docs/cli_agent_delegation.md` (created in M5) for the operational guidance. **Apply the four-check IA pass** to the edited skill body before saving (Scoping / Duplication / Configurability / Hierarchy per lesson `0004`). | `src/templates/skills/develop.md.j2` | 2 | done |
| 4.2 | Render-snapshot test: rendered develop body (a) names no specific agent in Phase 3 step 3 (no `booping-developer` literal), (b) contains the worker-pick clause in Phase 1, (c) contains both type-branches in Phase 3 step 3. | `booping-python/tests/commands/render_test.py` (extend) or new sibling `develop_render_test.py` | 1 | done |

#### Task 4.1 DoD

- [x] Phase 3 step 3 contains no literal `booping-developer` reference.
- [x] Phase 1 includes the multi-worker AskUserQuestion clause with the explicit "in-session, no plan-file persistence" wording.
- [x] Both invocation branches (native via `Agent` tool, cli via `booping run-agent`) explicit in Phase 3 step 3.
- [x] No mention of the underlying cli `command` in the skill body.
- [x] Long-running invocation note links to the M5 doc.
- [x] Four-check IA pass run on the edited skill body; pass notes recorded in the PR / sprint description.

#### Task 4.2 DoD

- [x] Tests assert the two structural properties listed in task 4.1.
- [x] `just test` exits 0.

---

### M5: Docs + CLAUDE.md + `src/files/` thin-shell rebuild — 1 SP | done

**Goal**: User-facing doc on declaring a cli worker + disabling internal agents; CLAUDE.md updated where the schema is described; `just build` re-renders thin shells if any frontmatter touched (none expected, but verify).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Write `docs/cli_agent_delegation.md` — covers: schema (`type`, `command`, `internal`, `disable_internal_agents`), `booping run-agent` invocation contract, **`command` Jinja2 template + `{{ prompt }}` placeholder semantics** (with examples: simple `pi --print` no-placeholder, explicit placement, stdin pipe via `sh -c`), final-prompt composition (extension first, separator `\n\n---\n\n`, briefing after — briefing-only when extension absent), the **v1 limitation** (cli agents have no rendered body equivalent of `_developer_body.j2`; the extension file at `_booping/agent_<id>.md` carries the full role context — workflow, hard rules, report format), pi-bundle example, long-running command guidance (Bash `run_in_background` + polling). Lazy-link from `develop.md.j2` and from CLAUDE.md's "Config schema" section. | `docs/cli_agent_delegation.md`, `CLAUDE.md` | 1 | done |

#### Task 5.1 DoD

- [x] `docs/cli_agent_delegation.md` exists and covers all bullets in the task description.
- [x] CLAUDE.md "Config schema (`src/config.yaml`)" subsection mentions the new `type` / `command` / `internal` keys and the per-skill `disable_internal_agents` flag, with a link to the new doc.
- [x] CLAUDE.md "Information ownership" section is reviewed; no contradiction with the new schema.
- [x] `just build` exits clean (no thin-shell drift).

---

### M6: Manual prose reshape — pause for review — 1 SP | pending

**Goal**: hand the rendered `develop.md.j2` + `_available_agents.j2` outputs back to the user for an IA pass before transitioning out. Apply any user-requested wording / structure tweaks in-place.

**Verify**: user explicitly approves the rendered shapes; `just build` + `bin/booping render` re-checked clean after final tweaks.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Render `bin/booping render src/templates/skills/develop.md.j2` and `bin/booping render src/templates/_partials/_available_agents.j2` (via a minimal harness) under (a) default config and (b) a fixture project override with cli entry + `disable_internal_agents: true`. Present both to the user. Apply requested edits to the templates / config; re-render until approved. | `src/templates/skills/develop.md.j2`, `src/templates/_partials/_available_agents.j2`, `src/config.yaml` | 1 | pending |

#### Task 6.1 DoD

- [ ] Both rendered outputs shown to the user under both fixture configs.
- [ ] All requested edits applied and re-rendered.
- [ ] User explicit approval captured.

---

## Final Verification

- [ ] `just lint` exits 0.
- [ ] `just typecheck` exits 0.
- [ ] `just test` exits 0.
- [ ] `just build` exits 0 with no unexpected thin-shell drift (`git diff -- skills/ agents/` clean).
- [ ] `bin/booping render src/templates/skills/develop.md.j2` produces clean output under default config.
- [ ] `bin/booping debug-context` against a fixture project override (cli entry + `disable_internal_agents: true`) shows the filtered, validated config.
- [ ] Manual e2e: with `pi` installed and a fixture project config pointing at it, `echo 'noop' | booping run-agent pi-test` exec's the command and round-trips the prompt (smoke check — full mesh pipeline out of scope).

## Out of scope

- Groom, retro, code-review, chat `agents` blocks — left native-only.
- `booping-researcher` cli-isation — researcher stays native everywhere.
- Auto-injecting `--append-system-prompt <vault>/_booping/agent_<id>.md` into cli commands — extension reaches the worker via the final-prompt append; system-prompt injection is the user's call in their `command:`.
- pi-bundle installation / orchestrator-system.md / mesh-extension setup — user handles per the bundle's INSTALL.md.
- Symmetric `booping run-agent` for native agents — hard-errors instead; native goes through the `Agent` tool.
- Streaming / background invocation primitives in `booping run-agent` — Bash tool's `run_in_background` handles long-running invocations.

## CLAUDE.md impact

Update these sections to reflect the new schema and `/develop` behaviour:

- **Config schema (`src/config.yaml`)** — document `skills.<name>.agents.<id>.type`, `.command`, `.internal`, and `skills.<name>.disable_internal_agents`. Link to `docs/cli_agent_delegation.md`.
- **Information ownership → `src/config.yaml`** — note that delegate kind (native vs cli) is now config-driven.
- **CLI** — add `bin/booping run-agent <id>` to the subcommand list with one-line description.
- **Skill design → Agent wiring** — note that `/develop` may now delegate to a cli worker via `booping run-agent`; the extension channel (`_booping/agent_<id>.md`) is shared between native and cli paths.
