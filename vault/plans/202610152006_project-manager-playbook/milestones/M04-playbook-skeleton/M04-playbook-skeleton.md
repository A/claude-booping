---
id: "04"
title: "project-manager playbook — manifest, preamble, on-start and intake"
sp: 4
status: done
plan: "plans/202610152006_project-manager-playbook/index.md"
---

# M04: project-manager playbook — manifest, preamble, on-start and intake

`bin/booping render-playbook project-manager` renders a three-step playbook whose preamble sets the session loop and the mode, whose `on-start` opens with the short `booping status`, and whose `intake` files every request in a user message as an item verbatim.

**Scope**: create `playbooks/project-manager/`:

- `playbook.md` — frontmatter `name: project-manager`, `title: Project Manager`, `summary:` one line (the manager the user talks to: files requests as items and carries each through groom, develop, review and merge in the project's autonomy mode), `trigger:` (talking to the project's manager; "what is going on", "take the open items", a message carrying several requests), `jinja: true`, `inline_steps: true`, `requires_project: true`. Preamble, lean (rule/0006), rendered from config, never restating it: `Autonomy: {{ config.core.autonomy }}` and one line per mode on what stops (supervised: plan approval inside the inline groom and the merge gate; autonomous: nothing — every gate settled and logged with `booping defaults add`, `--target` the plan's `index.md` when one exists, else the item file); the session loop (every later user message → `intake`, then `work`; at the start of every turn while a run is live, `booping status runs` first); hard rules — the driver owns the vault, every commit (scoped staging by path, never `git add -A`) and every transition, workers edit repo code only; `booping run` is launched with the Bash tool's background mode, never `&`, and acked with `booping run ack` once its outcome is acted on; a question the manager cannot settle goes on the item with `booping items ask` and chat only names the sidecar; never push, deploy or release unless a project rule or runbook targeting `project-manager` says how; no item store, handoff file or status file of its own. Then `{% set playbook_agents = config.core.project_manager_playbook %}{% include "_partials/playbook_agents.md" %}` and `{% include "_partials/playbook_shared_instructions.md" %}`, as `playbooks/code-review/playbook.md` does.
- `playbook.yaml` — `graph:` `on-start: []`, `intake: [on-start]`, `work: [intake]`; no `states:`.
- `on-start/prompt.md` — frontmatter `summary:` + `review_gate: null`. Body: run `booping status` and post its lines verbatim; then name what to act on, in this order — unacked finished, failed or lost runs; items waiting on the user (point at their sidecars); plans at `ready-for-dev` (develop next), plans `done` without a code review (review next); open items. Supervised: propose the first action and wait for the user's message. Autonomous: start `work` on that list without waiting. A user message already present → `intake` first.
- `intake/prompt.md` — frontmatter `summary:` + `review_gate: null`. Body: split the message into requests — each distinct ask, asides included; a message that only answers a pending question or confirms a gate is no request. Per request one `booping items add --source request --title "{short title}" --text -` with the user's own words for that request on stdin, character for character, never paraphrased; an answer to an item's question goes through `booping items answer {id} C{n} --text -` with the user's words; then post the filed ids, one line each `{id} {title}`.
- `src/config.yaml` — `core.project_manager_playbook.agents` with `booping-developer` (tiny fixes and review fixes) and `booping-researcher`, shaped and commented like `core.develop_playbook.agents`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Manifest, preamble and graph. | `playbooks/project-manager/playbook.md`, `playbooks/project-manager/playbook.yaml` | 2 | done |
| 4.2 | `on-start` and `intake` step prompts. | `playbooks/project-manager/on-start/prompt.md`, `playbooks/project-manager/intake/prompt.md` | 1 | done |
| 4.3 | `core.project_manager_playbook.agents` config. | `src/config.yaml` | 1 | done |

## Definition of Done

### Task 4.1

- [x] `bin/booping render-playbook project-manager` prints no STOP or Note notice, the step table lists `on-start`, `intake`, `work` in that order, and no `## State` section.
- [x] The preamble renders the autonomy value from config; no status, queue or agent id is written as a literal that config or a query already holds.

### Task 4.2

- [x] `intake` names `booping items add --source request … --text -` and `booping items answer`; it never paraphrases the user's words.
- [x] `on-start` starts with `booping status` and lists the act-on order above.

### Task 4.3

- [x] `bin/booping config-get core.project_manager_playbook.agents` prints both agents; the rendered playbook shows the agents table.

Return: the list of changed and created files, nothing else.

## References

- `playbooks/specs/playbook.md`, `playbooks/specs/guide/prompt.md` — an inline-steps playbook with no run state of its own and its step shape.
- `playbooks/code-review/playbook.md` — the agents and shared-instructions includes.
- `src/config.yaml` `core.develop_playbook.agents` — the agents block shape.

## Verify

`bin/booping render-playbook project-manager`
