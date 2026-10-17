**Request**

> Чем заменить: frontmatter-update size=M
> Что теряем: проверку по списку размеров - можем добавить настройку же. Единственное, давай по playbook-transition - подумаем над неймингом. Ну и может весь сет операторов осмыслить чтобы он не путал. scan - тут чуть больше подумай, но как будто терпимо. create может какой-то флаг иметь или свой макрос как ты предложил

> move - не нравится, как будто файл перемещается transite, хотя бы или подумай сам. остальное ок. загрумь и сделай плиз

> по items тоже ок

**Task type** — `feature`: new user-facing CLI verbs (`set`, `transition`, `state`, `config`) and a new template global (`next_id`) replace existing commands. Not `refactoring`: the command surface users and playbooks call changes. Not `bug`: nothing diverges from expected behaviour.

**Problem** — Operations on vault files are spread over commands named each its own way: `frontmatter-update`, `marker-set`, `playbook-transition`, `playbook-state`, `config-get`, plus `booping items` with eight verbs (add, list, plan, close, reopen, size, batch, scan) that mostly restate what `create`, `query`, `frontmatter-update` and `playbook-transition` already do. A fresh model given names only re-invents mechanisms (reference/0009). Target: one vocabulary — `create`, `query`, `set`, `transition`, `state`, `config` — and `booping items` gone, its verbs expressed through those, ids from a `next_id` template global, sizes checked by an mdcheck schema, `scan` moved to `booping specs scan`.

**Clarifications and Decisions**

- `booping set <file> k=v…` replaces `frontmatter-update` and `marker-set`; it writes frontmatter of a markdown file or keys of the `.booping` marker by file type (owner, "остальное ок").
- `booping transition <file> <status>` replaces `playbook-transition`; the machine is inferred from the machines whose `artifact` pattern matches the file and whose current status has an edge to `<status>`; `--state` and `--target` stay for a manual choice and for machines without `artifact:` (owner: "transite, хотя бы или подумай сам" — named `transition`).
- `booping state <file>` replaces `playbook-state`; `booping config <key>` replaces `config-get`; `create`, `query`, `render`, `render-playbook` stay (owner, "остальное ок").
- `create` gains a template global `next_id(prefix, width)` — the highest numbered file with that prefix in the destination plus one; open items, corrections and agent decisions use it (owner: "свой макрос как ты предложил").
- `booping items` goes: add → `create` with `next_id`; list → `query` on the existing index spec; size → `set size=…`, sizes checked by an mdcheck schema whose enum comes from config; plan / close / reopen → `set plan=…` + `transition`; the bulk `--plan` form the `open-items-follow-plan` hook uses → the script doing `query` + `transition`; batch → prose in the project-manager over `query`; scan → `booping specs scan` (owner: "по items тоже ок").
- No aliases or shims — release 2.0.0.
- The run is autonomous: groom and develop without stopping (owner: "загрумь и сделай плиз").
