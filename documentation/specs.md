# Specs

Specs are typed records of what the code cannot show: why a project exists and what it is like (values), the constraints every decision obeys (rules), the decisions with their rejected alternatives (ADRs), and the conflicts, stories, ideas, references and runbooks around them. Plain markdown with YAML frontmatter, one record per file.

## Format in brief

A tier root holds one directory per type and each record is a file `<type>/<NNNN>-<slug>.md`: a four-digit number running within the type and a kebab-case slug. A record is referred to as `<type>/<NNNN>` (`adr/0001`); in a body, references are ordinary relative markdown links.

The full format — frontmatter keys, the body sections each type requires, marks for open questions — is the shipped guide: [`src/specs/README.md`](https://github.com/A/claude-booping/blob/master/src/specs/README.md). Each type's shape is an [mdcheck](https://github.com/A/markdown-checker) rule file beside it under `src/specs/schemas/`.

booping ships eight types — `value`, `rule`, `adr`, `conflict`, `story`, `idea`, `reference`, `runbook` — and a tier can override or add to them (see [Tier schemas and tags](#tier-schemas-and-tags)), so a tier's types are whatever its effective schema set holds.

Write a record's content in any language, but keep its structural headings, bold labels, table columns and frontmatter keys the shipped English ones: one schema set serves every tier.

## Tier schemas and tags

A tier root can carry two files of its own beside its type directories:

- **`_schemas/<type>.yaml`** — an mdcheck rule file. A type the shipped set has gets this shape instead in this tier; a new name adds a type, whose records go in `<type>/`. It applies to that tier only — a global-tier schema never reaches a project. Use it for your own types and fields, not to translate headings.
- **`tags.yaml`** — a mapping `tag: one-line description`. Once it exists, every record's optional `tags:` list must use its keys: `area` or `area:sub` in kebab-case, with `area` itself listed for every `area:sub`.

A tier schema must keep the frontmatter keys and values booping reads — `type`, `status`, `kind`, `targets`, `brief`, `values`, `rules`, `supersedes`, `sources`, `reviewed`, `created_by`, and an ADR's alternatives status cell — as they are.

## Tiers

Specs come in three tiers, each a tier root of its own:

| Tier      | Where                                                                                     | Holds                                            |
|-----------|-------------------------------------------------------------------------------------------|--------------------------------------------------|
| `core`    | shipped with the plugin, at `specs/`                                                      | booping's rules for every project                |
| `global`  | `<home_dir>/_specs/`                                                                      | your values and rules for every project          |
| `project` | the vault root, type directories beside `plans/`; or a repo directory you choose          | the project's own records                        |

At the vault root only the type directories are records; plans, retrospectives and everything else in the vault are left alone. To keep the project's records in the repo instead, set the project tier's `path` — `booping specs init` links it into the vault as `<vault>/specs`. A vault that still holds its records under `<vault>/specs/` is moved to the root by `/playbook migrate`, which leaves a tier you pointed at the repo where it is.

Where each tier lives and what it is called is the [`core.specs`](project_config.md#corespecs) config key. The [setup playbook](install.md#scaffold-the-project-vault) sets up the global and project tiers and asks for your global namespace; [`booping specs init`](#booping-specs-init) creates either one on demand.

## Namespaced refs

A reference without a namespace points into its own tier: `rule/0003`. A reference into another tier names that tier's namespace in front: `booping:rule/0003` for core, `<user>:rule/0003` for the global tier, where the namespace is the one you gave setup — your `$USER` when none is set. A project that departs from a rule of a tier above records that in its own ADR or conflict, citing the rule by its namespaced ref.

## Injection

An accepted rule carrying `targets:` and `brief:` is injected into the playbooks, steps, agents and skills it targets, from all three tiers: each surface gets a `## Rules` section listing the brief of every matching rule with a link to its record. Target forms, the section shape, the ref and link per tier and the `--no-rules` opt-out are in [Playbooks → Rules](playbook.md#rules).

## Open items

A gap between the records and the code — an unconfirmed ADR, a `[clarify]` mark, a check finding — is filed as an open item, a file under `open-items/` in the vault that a plan can pick up and close; so is a request you file in your own words. The [specs playbook](specs_playbook.md#open-items) files and works them, and `booping items` drives them directly.

## Commands

Every verb but `site` takes `--tier core|global|project`, default `project`.

### `booping specs init`

```
booping specs init [--tier global|project]
```

Creates the tier root and its `README.md` when absent. The default project tier is the vault root, so there `init` creates nothing and prints only the root. A project tier kept in the repo is created there and linked from `<vault>/specs`, so the records sit with the code and stay reachable from the vault. Safe to re-run: it changes only what is missing.

Prints one line per change, in the order made, then the absolute tier root as the last line — on a re-run with nothing to do, only that last line. For a project tier kept at `specs/` in the repo:

```
created dir /home/me/Dev/app/specs
created file /home/me/Dev/app/specs/README.md
linked /home/me/Claude/app/specs -> /home/me/Dev/app/specs
/home/me/Dev/app/specs
```

The `core` tier ships with the plugin and is never created. An error prints `specs init: {message}` on stderr — the core tier asked for, a path in the way that is not a directory, or a `<vault>/specs` that is not a link to the tier — and nothing is written.

### `booping specs ls`

```
booping specs ls [--tier TIER] [--type TYPE]
```

Lists the tier's records, one per line: `{type}/{NNNN}  {status}  {summary}`, sorted by type and number. `--type` keeps one type.

### `booping specs next`

```
booping specs next TYPE [--tier TIER]
```

Prints the next free ref of a type in the tier — the highest number plus one, e.g. `adr/0004`. Use it to name a new record.

### `booping specs check`

```
booping specs check [--tier TIER]
```

Validates every record of the tier: its type's schema (the tier's own from `_schemas/` when it has one), the directory layout and file names, unique numbers, frontmatter, rule targets, relative link targets, typed refs, `sources` paths, `tags` against the tier's `tags.yaml`, and each ADR's alternatives — every table row matches one `###` option and exactly one option is accepted (at most one while the ADR is not accepted or superseded). A tier schema mdcheck cannot load is reported as an error on that file. Each finding prints as `{path}:{line}  {level}  {check}  {message}`, followed by a count on stderr. A cross-tier ref whose namespace no configured tier answers to, or whose tier is absent on this machine, is a warning, not an error.

The check needs the `mdcheck` binary on `PATH`:

```
cargo install markdown-checker --version 0.1.2 --locked
```

### `booping specs site`

```
booping specs site [--out DIR] [--root NAME=PATH ...] [--title TEXT] [--site-url URL]
```

Renders one or several specs roots to a static HTML site you open in a browser straight from disk: no server and no network — fonts, icons and styles ship inside the output. The same input always produces a byte-identical tree.

- **`--out DIR`** — the output directory, default `specs-site` in the working directory.
- **`--root NAME=PATH`** — a root to render, repeatable: a name (`[A-Za-z0-9][A-Za-z0-9._-]*`) and a directory holding type directories. `~` is expanded. Default: the tier and configured roots, below.
- **`--title TEXT`** — the site title, shown in the header and in every page's `<title>`; default the attached project's name, else `Specs`.
- **`--site-url URL`** — the public `http://` or `https://` URL the site is served at; default none. Given, the build also writes `404.html` (below).

**Root selection.** Given `--root` at least once, exactly those roots are rendered, in the order given. Otherwise the roots are the three [tiers](#tiers) — core, global, project, each named by its namespace, the project tier by the project's name — followed by every entry of [`core.specs.site.roots`](project_config.md#corespecs). A tier whose directory does not exist is left out silently; a configured root whose directory does not exist is skipped with a warning. A root resolving to a directory already selected is skipped, so a tier that is also a configured root renders once. A root's name is its namespace on the site: `name:type/NNNN` refs resolve against it, so give a configured root the namespace its records are cited by.

To build one site over every project's specs, list them in the global config and run the command from `home_dir`:

```yaml
# ~/.config/booping/config.yaml
home_dir: ~/Claude
core:
  specs:
    site:
      roots:
        - {name: app, path: ../Dev/app/specs}
        - {name: api, path: /home/me/Dev/api/specs}
```

A `path` is absolute, `~`-prefixed, or relative to `home_dir`.

**Page shell.** Every page has a skip link, a header with the site title (linking home) and a theme toggle, a sidebar, breadcrumbs, and a footer naming the generator — no build date, so rebuilds stay byte-identical. The theme toggle cycles auto → light → dark and remembers the choice in the browser; auto follows the system setting. Text is set in Golos Text, code in JetBrains Mono, both Cyrillic and Latin. Below 760px wide the layout drops to one column, list rows become cards, the filter chips scroll on one line, and the sidebar moves into a drawer opened from a menu button; without JavaScript the sidebar renders in the page flow instead, and every page still reads.

The sidebar, top to bottom: Overview; **Review** with the number of rows waiting for you; **All records** with the total; **Types** — every type that has records, across roots, with its count, each opening All records filtered to it; **Tags** — for each root with tags, its top-level tags that records carry, as plain links with counts, and a link to the root's tag tree (the root's name as a sub-heading when more than one root has tags); **Sources** — each root with its record count; and `llms.txt`.

**Pages.**

- `index.html` — home: the site title; the first value record's summary as the lead; when anything waits for you, one callout linking the review page (`3 need you →`) followed by the number of unreviewed records and of open `[clarify]` questions, a zero count left out (`3 need you → · 2 unreviewed · 1 open question`); a card per type with records — name, count and a one-line scenario ("why the project exists" for values) — opening All records filtered to that type; and **Recently updated**, the ten records with the latest `updated_at`. The title, lead, callout and Recently updated sit in one reading column; the cards span the full width.
- `review.html` — everything that needs you, as a filterable list (below).
- `records.html` — every record of every root, as a filterable list.
- `{root}/index.html` — the root's types, each with its name, record count and scenario, then every `[clarify]` and `[unknown]` mark in the root, each linking to its line in the record.
- `{root}/{type}/index.html` — the type's scenario, then a filterable list of its records.
- `{root}/tags/index.html` — the root's tag tree: every tag nested under its parent (`area` above `area:sub`), with its description and the number of records carrying it or any tag below it. Written only for a root that has tags.
- `{root}/tags/{tag}.html` — one tag, its `:` written as `.` (`area:sub` → `area.sub.html`): breadcrumbs through its parent tags, the description, the tags below it, then a filterable list of every record carrying the tag or one below it.
- `{root}/{type}/{NNNN-slug}.html` — one record: title, state badges, tags linking to their tag pages, summary, then labelled facts — author, created, updated, reviewed, sources — with dates written out in the site's language, then, as rows of the same facts list, every relation (`values`, `rules`, `supersedes`, …) as titled links with the target's status, plus **Superseded by** when a later record supersedes this one, any other frontmatter key, the body, and **Referenced by** — every record linking to this one, across roots — all in one reading column. Around the body:
  - **On this page** — a rail beside the text, at 1100px and wider, listing the body's `##` sections with their `###` sections nested, then Referenced by, and highlighting the section you are reading as you scroll. When the body holds `[clarify]` or `[unknown]` marks, an **Open questions** block below it lists each mark — clarify first — linking to its line. The rail shows when the body has a `##` or `###` heading or any mark; narrower screens get the same blocks in a collapsed panel under the summary.
  - **`§` section links** — every `##` to `####` heading, and Referenced by, ends with a `§` link to itself, shown on hover or focus (always on touch screens). Clicking it moves the address to that section and copies the full link to the clipboard, `file://` included; a collapsed panel holding the target opens itself.
  - **Referenced by, grouped** — the citing records under one heading per type, each followed by *via*: the frontmatter relations naming this record (`Rules`, …) and the `##` sections of the citing record whose text links here. When a link points at one of this record's own sections (`…/0003-x.md#decision`), a **By section** block lists those sections with the records citing each.
  - **ADR option cards** — in an `adr` whose `## Alternatives` holds the shipped options table (Option, Status, Complexity, Reversibility, Verdict) the table stays as the summary, the accepted option's row marked **chosen**, and each `###` option becomes a card: status, complexity and reversibility from its table row, then the verdict and the option's own text. Accepted options come first and open, the rest collapsed in written order; below 760px the table is hidden and the cards carry it. An Alternatives section of any other shape renders as written.
- `search.html` — every search result for the query in its address, `search.html?q=…` (below).

A row in a list shows the record's ref, its title linking to the record page, its state badges and its summary.

A root's tags are the keys of its `tags.yaml` (see [Tier schemas and tags](#tier-schemas-and-tags)), every tag its records carry, and each of those tags' parents; a tag's description comes from `tags.yaml` and is empty for a tag the file does not list. A `tags.yaml` that does not parse prints one warning and the tree is built from the tags the records carry.

**Filters.** A list page carries chips above the rows, grouped by facet — **Type**, **Source** (the root), **Status**, **Needs** — each chip showing how many rows on the page carry its value; a facet with only one value shows no chips, except Needs. Chips in one facet widen the list (any of them), chips in different facets narrow it (all facets). A sort menu orders the rows by number (the default), most recently updated, or title; the count below the chips says how many rows are shown. The state lives in the address, so a filtered list is a link you can share or bookmark:

- `records.html#type=rule` — the rules only;
- `records.html#source=api` — the records of root `api`;
- `records.html#status=accepted,proposed` — accepted or proposed records;
- `records.html#flag=clarify` — records with a `[clarify]` mark;
- `records.html#type=adr&status=accepted&sort=updated` — accepted ADRs, newest first.

Keys come in the order `type`, `source`, `status`, `flag`, then `sort` when it is not the page's default; several values of one key are comma-separated. A key or value the page does not know is ignored. Without JavaScript the chips are hidden and every row stays listed.

**Search.** Every page's header carries a search box; press `/` anywhere outside a text field to jump into it. Typing opens a dropdown of the first eight matches — ref, title, status — and a last line, **All results →**, opening `search.html?q=…`. Down and Up move through the list, Enter opens the highlighted result or, with none highlighted, the results page; Esc closes the list, a second Esc clears the box. Below 760px the box gives way to a search button in the header that opens it full-screen; Esc or the close button returns you to the page. `search.html` lists every match as list rows with their summary and a count.

Matching ignores case and treats `ё` as `е`. A query word matches a record field when a word of the field starts with the query word minus a crude ending (a word longer than seven letters loses its last three, longer than five its last two), so `решени` finds «Решение» and `елка` finds «Ёлка». Every query word must match somewhere. Results rank by where they matched — ref, then title, tags, summary, body — and then in All records order.

The data lives in two files at the site root: `search-index.js` (each record's ref, title, summary, status, tags and page) and `search-body.js` (each record's body as plain text). A page loads them only when you first use the box — the body file once you type — as plain `<script>` files, so search works from `file://` with no server. Without JavaScript the box submits to `search.html`, which says that search needs JavaScript and links All records.

**Review.** `review.html` lists every record that needs you, in All records order, each row showing why with its badges — the clarify and unknown badges link straight to the first such mark in the record. A record is listed when any of these holds, and each is a **Needs** chip on the page:

- **Unreviewed** — `reviewed` is not set;
- **Has [clarify]** / **Has [unknown]** — the body holds such a mark;
- **Open conflict** — a `conflict` record with status `open`;
- **Proposed ADR** — an `adr` with status `proposed`;
- **Open** — an `idea` with status `open`, or an open item.

When the site renders its default roots for a project with a vault, the vault's [open items](#open-items) with status `open` follow the records — the item's id and title, linking to the record it names when that record is on the site. The review page sorts by **Review order** by default: what the agent wrote first, then the oldest by `updated_at`; it also offers the other sorts. With nothing to review it says so. The sidebar's Review count and the home callout are the number of rows on this page.

**State badges.** Each badge carries an icon and text, never colour alone: the record's status (`accepted`, `proposed`, …), the count of `[clarify]` marks (`2 questions for you`, linking to the first mark on a record page), `[unknown]` when the body has one, and `unreviewed` when `reviewed` is not set.

Relative links and typed refs between records become links to the target's page, across roots too. A link to something that is not a record renders as plain text; a link or ref whose target is missing renders as plain text and prints a warning. The site never fails on a link — `booping specs check` is the validator.

**Language and labels.** Page text — UI strings, type names and scenarios, statuses, fact names, author names and month names — comes from the label table for `core.specs.site.lang` (default `en`; `en` and `ru` ship), which also sets `<html lang>`. A project whose records are written in another language sets it in its vault config — content language is not detected, so a Russian vault left on the default publishes Russian text under `lang="en"`. A language with no table renders with English labels, keeps its `<html lang>` and prints one warning. `core.specs.site.labels.{lang}` overrides or adds labels key by key through the usual config merge, falling back to `en` and then to the raw id, so a project names its own types without restating the rest. A project tier with a `_schemas/mechanic.yaml` type, published in Russian:

```yaml
# {vault}/config.yaml
core:
  specs:
    site:
      lang: ru
      labels:
        ru:
          types:
            mechanic: {name: Механика, plural: Механики, scenario: "Механики — как устроен мир"}
```

A label holding counts is a list of plural forms: two (one, other) or three (the Slavic one, few, many), as in `clarify: ["{n} вопрос к тебе", "{n} вопроса к тебе", "{n} вопросов к тебе"]`. `booping config-get core.specs.site.labels.en` prints every key with its shipped value.

**Output directory.** Besides the pages, every build writes:

- `style.css`, `site.js` (theme toggle and drawer), `fonts.css` with the fonts embedded — so nested pages opened from `file://` render them too — and the fonts' OFL licences under `fonts/`;
- `search.js`, `search-index.js` and `search-body.js` — the [search](#booping-specs-site) and its data;
- `{root}/{type}/{NNNN-slug}.md` — each record's source file, byte for byte, linked from its page as the Markdown alternate;
- `llms.txt` — the site in the [llms.txt](https://llmstxt.org/) shape: the title, the first value's summary, then one section per root and type with a line per record linking its `.md` copy, with its summary, status and tags;
- `index.json` — the title, the language and every record's metadata in page order: id (`{root}:{ref}`), type, title, summary, status, tags, author and dates, page and `.md` paths, mark counts, relations, superseded-by and backlinks as ids;
- `404.html`, only with `--site-url` — a not-found page whose links resolve against the URL's path, so it works at any depth the host serves it from;
- the `.booping-site` marker.

The command refuses — and writes nothing — when the out path is a file, lies inside one of the rendered roots, or is a non-empty directory without the marker. A directory carrying the marker is cleared and rewritten, so re-running into the same `--out` is safe.

**Output.** On success, stdout gets one line:

```
specs site: 3 roots, 42 records, 51 pages, 2 warnings -> specs-site
```

Warnings go to stderr, sorted by path then line:

```
/home/me/Dev/old/specs  warning  site  root old not found, skipped
vault/adr/0002-ports.md:5  warning  site  unresolved ref booping:rule/0099
vault/adr/0002-ports.md:14  warning  site  unresolved link ../rule/0099-gone.md
```

An error prints one `error: {message}` line on stderr.

### `booping specs site-index`

```
booping specs site-index [--projects PATH|-] [--out DIR] [--title TEXT]
```

Renders one index page in the site's design that links to several projects' specs sites — the page at the root of a [GitLab Pages group](#publishing-on-gitlab-pages). Reads no specs root; its language and labels come from `core.specs.site.lang` and `core.specs.site.labels`, as for [`booping specs site`](#booping-specs-site). The same input always produces a byte-identical tree.

- **`--projects PATH|-`** — the project list, default `-`: `-` reads it as JSON from stdin, a path reads the file as YAML.
- **`--out DIR`** — the output directory, default `specs-site-index` in the working directory.
- **`--title TEXT`** — the site title in the header, the page heading, its single crumb and its `<title>`, default `Specs`.

**Input.** A list of entries, each a mapping with exactly these keys:

- `name` — required, a non-empty string, unique across the list.
- `url` — required, starting `http://` or `https://`.
- `description` — optional, a string or null.

Any other key, a top level that is not a list, an entry that is not a mapping, and every violation above is an error naming the entry by its 0-based position in the input (`projects[3]: …`); so is unreadable input — a missing file or a YAML or JSON syntax error.

**Page.** The same shell as a site page — skip link, header with the theme toggle, breadcrumbs, footer — without the sidebar. The heading, then one row per entry: the name linking to its URL, its description below. Rows are sorted by name, case-insensitively; input order never shows. A description's whitespace — newlines included — collapses to single spaces, so each renders on one line; a missing or null description leaves the row with the name only. An empty list renders the heading and `No projects.` (in the configured language) and still succeeds.

**Output directory.** `index.html`, the site's `style.css`, `site.js`, `fonts.css` and font licences, and the `.booping-site` marker, under the same rules as [`booping specs site`](#booping-specs-site): a non-empty directory without the marker is refused, one carrying it is cleared and rewritten.

**Output.** Piping a two-project list on stdin:

```json
[
  {"name": "api", "url": "https://{group}.{pages-domain}/api", "description": "Payments API."},
  {"name": "app", "url": "https://{group}.{pages-domain}/app", "description": null}
]
```

```
$ booping specs site-index --out public < projects.json
specs site-index: 2 projects -> public
```

An error prints one `error: {message}` line on stderr and writes nothing.

### Exit codes

| Code | `init`                                                     | `ls`, `next`                                                   | `check`                                                        | `site` | `site-index` |
|------|------------------------------------------------------------|----------------------------------------------------------------|----------------------------------------------------------------|------|------|
| 0    | tier in place                                              | printed                                                        | no errors (warnings may be printed)                            | site written (warnings may be printed) | index written |
| 1    | the tier is `core` or unavailable, or a path is in the way | unknown type, or the tier is unavailable or has no directory   | at least one error, or the tier is unavailable or has no directory | a malformed `--root` or one that is not a directory, a bad configured root entry, duplicate root names, no roots, a `--site-url` that is not `http(s)`, or the out directory refused | an unreadable or invalid project list, or the out directory refused |
| 2    | config could not be loaded                                 | config could not be loaded                                     | the check could not run: config not loaded, `mdcheck` missing or failing | config could not be loaded | config could not be loaded |

## Publishing on GitLab Pages

Each project publishes its own specs site on GitLab Pages, and one index project at the group's Pages root lists every project of the group carrying a topic, linking to each site. booping ships both CI jobs as templates a project includes by URL.

**A project's site.** The project keeps its specs in a [repo-local vault](vault.md#booping). Its `.gitlab-ci.yml` includes the site template, which adds a `pages` job on the default branch running `booping specs site --out public --site-url "$CI_PAGES_URL"` — so the site gets its `404.html`:

```yaml
include:
  - remote: https://raw.githubusercontent.com/A/claude-booping/master/src/ci/gitlab/specs-site.gitlab-ci.yml

pages:
  variables:
    BOOPING_REF: v1.1.1  # a release tag
```

`BOOPING_REF` defaults to `master`; pin it to a release tag so a booping change reaches the site only when you move the pin. `BOOPING_REPO` overrides the clone URL. The site is served at `https://{group}.{pages-domain}/{project}`.

**The index.** Create a project named `{group}.{pages-domain}` in the group — GitLab serves its Pages at the group's Pages root, `https://{group}.{pages-domain}/`. Its `.gitlab-ci.yml` includes the index template:

```yaml
include:
  - remote: https://raw.githubusercontent.com/A/claude-booping/master/src/ci/gitlab/specs-index.gitlab-ci.yml
```

Then, in that project's settings:

- a project access token with the `read_api` scope, stored as the masked CI variable `SPECS_INDEX_TOKEN`;
- a pipeline schedule — the job runs on a schedule and on a manual pipeline run, never on push.

The job lists the group's non-archived projects carrying the topic through the GitLab API and pipes them into `booping specs site-index --projects - --out public`. Optional variables:

- `SPECS_TOPIC` — the topic that marks a project for the index, default `booping-specs`.
- `SPECS_PAGES_BASE` — optional fallback base URL (`{base}/{project path}`) for a project whose Pages URL the API does not return; normally each project's link is its own Pages URL from `GET /projects/:id/pages`, so unique Pages domains work. A project without Pages is left out of the index.

**Adding a project** to the index is setting the topic on it; the next scheduled run lists it.

**How the jobs get booping.** Both run on the `ghcr.io/astral-sh/uv:python3.12-trixie` image, which carries uv, Python and git, shallow-clone booping at `BOOPING_REF` and run its `bin/booping`; the uv cache is kept between runs. Neither job needs `mdcheck` — only `booping specs check` does. A project adding its own `specs check` job installs it with:

```
cargo install markdown-checker --version 0.1.2 --locked
```

**Limits.** Projects in subgroups are not listed — only the group's own projects. Archived projects are skipped.
