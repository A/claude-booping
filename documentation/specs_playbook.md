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

- `request` — your own words, filed as you said them; `backlog` — a task put aside for later. Neither has a direction (`direction: null`); the body is the text exactly as given, and without a `--title` the title is its first sentence.
- `manual`, `adr`, `mark`, `check`, `sync`, `correction` (a logged correction that names a spec record) — a specs-to-code gap, with a `direction`: `code-to-spec`, `spec-to-code`, `conflict` or `clarify`.

An item moves `open` → `planned` → `done`, or straight from `open` to `done` when it is settled without a plan, or to `dropped` when it needs no work; a planned item can go back to `open`. An open item that asks you a question waits in `clarify` until the answer is in its body, then returns to `open`. Closed items stay on disk with `closed_at` and `reason`, out of the default list.

### `booping items`

Run anywhere inside a booping project; paths print vault-relative.

| Verb | What it does |
|------|--------------|
| `list [--all]` | The index as a table — `id`, `status`, `source`, `direction`, `record`, `title`, `plan`; every non-terminal item (`open`, `clarify`, `planned`), every item with `--all`. |
| `add --text TEXT [--title TEXT] [--source request\|backlog]` | Files a request (the default) or backlog item with the text as its body, verbatim. `--text -` reads the text from stdin. |
| `add --title TEXT --direction D [--record REF] [--source S] [--text TEXT]` | Files a specs-to-code gap; `--direction` alone makes it `manual`. `add --record adr/NNNN` without `--title` takes the title from the ADR's `Confirmation:` line. |
| `scan [--tier T]` | Files one item per `[clarify]` / `[unknown]` mark and per `specs check` finding in the tier; an item already filed for the same thing is skipped. |
| `plan ID… --plan PATH` | Links open items to a plan and marks them planned. |
| `close ID… [--dropped] [--reason TEXT]` | Closes open or planned items as done, or as dropped with `--dropped`. `close --plan PATH` closes every planned item linked to that plan. |
| `reopen ID…` / `reopen --plan PATH` | Returns planned items to open and clears their plan. |

`booping items {verb} --help` lists every flag and its allowed values.

### Filing a request from anywhere

`booping items add --text -` reads the whole of stdin, so anything that can run a command can file a request — a shell script, a chat or mail bridge, a hook:

```sh
printf 'Ship the tracker sync.\nIt should run nightly.\n' | booping items add --text -
```

It prints the new item's path (`open-items/OI-NNNN.md`). The text lands byte for byte: blank lines, `---` lines, trailing spaces and template-looking `{{ }}` are kept as typed. Two items filed at the same moment always get different ids.

### Items and plans

Name the items in a groom request (`/playbook groom — work OI-0003 and OI-0007`) and groom links them to the new plan. From there they follow the plan: develop finishing it at `done` closes them, a failed or cancelled plan returns them to `open`. A plan cancelled some other way leaves its items planned — `booping items reopen --plan plans/{dir}/index.md` puts them back.
