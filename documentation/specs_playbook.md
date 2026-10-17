# specs playbook

Work the project's [specs](specs.md) records from one place: set up a tier, settle values, record decisions, ideas and rules, review the set, sync it with the code, and work the gaps between specs and code as **open items**.

```text
/playbook specs
```

## What it does

The playbook is a guide, not a menu: say what you want in plain words and it acts on it — it never asks which action to run. It reads the [specs format guide](specs.md#format-in-brief) before writing a record, numbers records with `booping specs next`, marks what it writes `created_by: claude` (never `reviewed` — that stays yours), and runs `booping specs check` after every write.

The scenarios it knows:

| Scenario | What happens |
|----------|--------------|
| Init | The repo has no project tier yet: it offers to create one with `booping specs init --tier project`, then walks you through the alignment guide. |
| Alignment | An interview that settles your values first, then the conflicts between them, then the rules that follow, then the decisions already made — one question at a time. |
| Auto-review | Reads the values, rules and ADRs for contradictions: one the records settle becomes a `conflict` record, one only you can settle becomes an open item. |
| Record | A decision becomes an ADR (only for one choice with a real alternative and a reason the code cannot show), an idea an idea record, a constraint on how the model works a rule with `targets` and `brief`. |
| Sync specs and code | Compares the records with the code; each gap becomes one open item with the direction it runs. |
| Retro to rules | A retrospective waiting for learning goes to the [learn playbook](learn.md); a lesson from the conversation becomes a rule directly. |
| Open items | Shows the open items so you can pick some to plan, drop or reopen. |
| Handed over | Another playbook's subagent hands over spec material or a question ([base guidance](specs.md#base-guidance-in-every-run)): it writes the material as a draft, or answers from the records, in at most five lines. |

Every scenario ends by naming the next call.

## Open items

An open item is one piece of work waiting in the vault: something you asked for, or a gap between the specs and the code — an ADR whose `Confirmation:` line the code does not show yet, a `[clarify]` or `[unknown]` mark in a record, a `booping specs check` finding, a conflict only you can settle, a gap a sync found. Each item is a file `open-items/OI-NNNN.md` in the vault, carrying a `title`, the `source` that filed it, a `direction`, the `record` it is about and the `plan` it is linked to.

The `source` says what kind of item it is:

- `request` — your own words, filed as you said them; `backlog` — a task put aside for later. Neither has a direction (`direction: null`); the body is the text exactly as given, under a short title.
- `manual`, `adr`, `mark`, `check`, `sync`, `correction` (a logged correction that names a spec record) — a specs-to-code gap, with a `direction`: `code-to-spec`, `spec-to-code`, `conflict` or `clarify`.

An item moves `open` → `planned` → `done`, or straight from `open` to `done` when it is settled without a plan, or to `dropped` when it needs no work; a planned item can go back to `open`. An open item that asks you a question waits in `clarify` until the answer is in its body, then returns to `open`. Closed items stay on disk with `closed_at` and `reason`, out of the default list.

### Working items from the shell

Items are ordinary vault files, worked with the same operators as everything else; run them anywhere inside a booping project.

| Operation | Command |
|-----------|---------|
| List | `booping query --config core.specs.open_items.index` — the index as a table, `id`, `status`, `source`, `size`, `direction`, `record`, `title`, `plan`; narrow it with `--where status:in=open,clarify,planned`. |
| File | `booping create core.specs.open_items.template {vault}/open-items --set title=… --set source=… [--set direction=…] [--set record=…] [--set body=…]` — the next free `OI-NNNN` is taken by `next_id`; a gap from an ADR passes `--set source=adr --set record=adr/NNNN --set direction=spec-to-code` and its `Confirmation:` line as the title. |
| Scan | `booping specs scan [--tier T]` — files one item per `[clarify]` / `[unknown]` mark and per `specs check` finding in the tier; an item already filed for the same thing is skipped. |
| Link to a plan | `booping set {item} plan=plans/{dir}/index.md`, then `booping transition {item} planned`. |
| Size | `booping set {item} size=S` — one of the `core.project_manager_playbook.batch` sizes, checked by `mdcheck playbooks/specs/_schemas/open_item.yaml {item}`. |
| Close | `booping transition {item} done`, or `dropped` for one needing no work — `booping set {item} reason=…` first to say why. |
| Reopen | `booping transition {item} open` — returns a planned item to open and clears its plan. |

### Filing a request from anywhere

`booping create` takes the text as a `--set` value, so anything that can run a command can file a request — a shell script, a chat or mail bridge, a hook:

```sh
booping create core.specs.open_items.template "$VAULT/open-items" \
  --set source=request --set title="Ship the tracker sync" \
  --set body="$(printf 'Ship the tracker sync.\nIt should run nightly.\n')"
```

It prints the new item as a diff (`+++ open-items/OI-NNNN.md`). The text lands as given: blank lines, `---` lines, trailing spaces and template-looking `{{ }}` are kept as typed.

### Items and plans

Name the items in a groom request (`/playbook groom — work OI-0003 and OI-0007`) and groom links them to the new plan. From there they follow the plan: develop finishing it at `done` closes them, a failed or cancelled plan returns them to `open`. A plan cancelled some other way leaves its items planned — `booping transition {item} open` on each puts them back.
