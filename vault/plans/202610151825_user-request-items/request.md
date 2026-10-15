# Request

**Request**

> groom the next part that the previous plans of this request (the latest done plans in vault/plans whose request names adr/0028) left out of scope as a parked follow-up.
>
> Request — the core `project-manager` playbook, as decided in vault/specs/adr/0028-one-project-manager.md (read it first; also adr/0024-0027, value/0015, and core rule/0030). Sources to fold in (read, do not copy project specifics): /home/anton/Dev/@A/notes/projects/hermes-pet/_playbooks/orchestrate/ (live manager session) and /home/anton/Dev/@A/notes/projects/_playbooks/backlog-run/ + backlog-manage/ (task state machine, budget and window gates, pause/resume, batching by size, question sidecars). Build on the open-items store that already exists in this branch (`booping specs open-items`, vault open-items/) — items get a `source` (user request verbatim, spec gap, backlog task); do not create a second store.
> Parts: (1) the item model extended for user requests (verbatim text, source) and `booping items add` usable by any channel; (2) a computed status report (code, not a stored handoff): open items by state, open ideas nobody took, plans, registered runs, unreviewed records and marks — short by default; (3) a run registry: every launched `claude -p` groom/develop run recorded with its item, wrapped by a `booping run groom|develop <plan> --autonomous` command that sets the env (`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`), `< /dev/null`, the autonomy preamble and a log file; (4) the project-manager playbook itself: supervised and autonomous modes (adr/0027), questions on the item, the request → items → groom → develop → independent review → fixes → merge → report loop, autonomous mode with backlog-run's budget/window gates and batching; (5) docs, and setup linking `<vault>/specs` to the repo's specs when the vault is outside the repo. Intake from messengers/ntfy, duplicate merging and tracker integrations are NOT core (adr/0028) — leave them out.
> (6) The project specs tier is the vault root (adr/0001 as amended 2026-10-15) … Do this part FIRST, before the project-manager parts, since they file items and read records.
> (0) Small fix first: plan 202610151609_autonomy-modes M05 made migrate's survey always ask about uncommitted work on the branch only in `playbooks/migrate/survey/opus-5.md`; the generic `prompt.md` (rendered in the committed report) lacks it — bring prompt.md in line (adr/0027), accept the migrate report drift that this exactly describes.

(Run directives — autonomous, worktree, snapshot policy — are in the session prompt and not repeated here. Parts (0) and (6) shipped in [202610151727_project-specs-at-vault-root](../202610151727_project-specs-at-vault-root/index.md); part (0)'s line is in `playbooks/migrate/survey/prompt.md:4`. This plan grooms part (1).)

**Task type** — `feature`: a new user-facing capability (filing a user's request as an item from any channel through a new top-level CLI group). Not `bug`: nothing observed diverges from documented behaviour — the store does what adr/0025 asked. Not `refactoring`: the change adds a source vocabulary, a stdin text path and a new command surface; behaviour visible to the user changes, so the no-behaviour-change test fails.

**Problem** — Today the item store (`open-items/OI-NNNN.md`, adr/0025) holds only spec gaps: `booping specs open-items add` requires `--direction` (code-to-spec, spec-to-code, conflict, clarify), `source` is a closed set of filing mechanisms (`manual`, `adr`, `mark`, `check`, `sync`, `correction`), the body comes from one `--body` argv flag, and ids are allocated as an unlocked max+1. adr/0028 makes this the one item store for the project-manager: a user request must be filable with the user's words verbatim and a source saying where it came from, by any channel (a chat session, a script, a bridge someone builds on top), through `booping items add`.

**Clarifications and Decisions** (autonomous run — every one is a default, logged in `clarifications.md`)

- C1 — one `source` field, extended: adds `request` and `backlog`; the existing mechanism values are the spec-gap sources. No second field.
- C2 — the command group moves to top-level `booping items` (add, list, plan, close, reopen, scan); `booping specs open-items` goes, every reference cleaned in this sprint. It never shipped in a tag.
- C3 — the verbatim text is the item body, passed by `--text TEXT` or `--text -` (stdin), written byte-for-byte; `--body` goes.
- C4 — `direction` is required for spec-gap sources and null for `request`/`backlog`.
- C5 — `--title` is optional for a request; absent, it is derived from the text's first sentence.
- C6 — ids are allocated by exclusive file create, retrying on a taken id, so concurrent channels never share an id.
- C7 — the index gains a `source` column.
- C8 — config key `core.specs.open_items`, the `open-items/` directory, `OI-` ids and the `open_item` machine stay where they are; no vault migration (every change is additive to item files).
- C9 — out: splitting one message into several items (the project-manager's judgement, part 4), questions on the item (part 4), a channel field, intake bridges, duplicate merging, trackers (adr/0028).
