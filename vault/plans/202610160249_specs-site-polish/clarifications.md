# Clarifications

## C1 — reading measure — answered

**Asked:** 2026-10-16 — intake

**Question:** The brief asks for a 68–70ch reading column and allows facts and relations to stay wider; the prototype wraps the whole record (header, facts, body, backlinks) in one 68ch column. Which width, and what goes inside it?

**Options:**

- The existing `.measure` token (68ch) around the whole record column and the home lead, callout and Recently updated — the prototype's shape
- Cap only body prose, leave facts, tables and option cards full width

**Answer:**

Default (autonomous run): the existing `.measure` token, 68ch, around the whole record column — header, facts, body, Referenced by — and around the home lead, callout and Recently updated; the home scenario cards stay full width as in the prototype. One column edge reads calmer than mixed widths, the token already exists (value/0003, single source), and the prototype the owner approved does exactly this. The ADR Alternatives table keeps its horizontal-scroll wrapper inside the narrower column.

## C2 — relations and the facts grid — answered

**Asked:** 2026-10-16 — intake

**Question:** "Relations align with the facts grid" — render them as rows of the facts `<dl>`, or keep a separate list whose columns line up with it?

**Options:**

- Rows of the facts `<dl>` — label in the `dt` column, the linked records (ref + state badge) in the `dd`, as the prototype's «Служит ценностям» row
- A separate `<dl>` with matching column widths

**Answer:**

Default (autonomous run): rows of the one facts `<dl>`, after Author/Created/Updated/Reviewed, each `dd` holding the existing `ul.rel` list (title link, ref, state badge) compacted to the facts font size. The prototype does this, and one grid aligns by construction where two grids only align by tuning. The separate raw-frontmatter box (`targets`, `brief` …) is not a relation and stays a separate box. The `.relations` section and its CSS are removed in the same milestone (booping:rule/0007).

## C3 — the home callout line — answered

**Asked:** 2026-10-16 — intake

**Question:** The brief: "the home callout should name what needs the owner (unreviewed + open questions) in one line", with ONE "N need you →" link. Exact content?

**Answer:**

Default (autonomous run), locked per booping:rule/0010: the link `{needs_you}` (existing label, unchanged) to `review.html`, then plain text parts joined by ` · `: `{unreviewed_n}` — new plural label, en `["{n} unreviewed", "{n} unreviewed"]`, ru `["{n} без ревью", "{n} без ревью", "{n} без ревью"]` — and the existing `{open_questions}`. A part whose count is 0 is omitted; with `needs` = 0 the callout is not rendered (as today). The `unreviewed` count is the records whose state is unreviewed. Example en: «115 need you → · 115 unreviewed · 12 open questions»; ru: «59 записей ждут тебя → · 59 без ревью · 3 открытых вопроса».

## C4 — sidebar tags — answered

**Asked:** 2026-10-16 — intake

**Question:** The sidebar tag tree renders every tag as a monospace `<code>` chip, including tags with 0 records (from `tags.yaml`); the brief says monospace only for record refs and code, and the prototype shows tags as plain sidebar links with a count. Change it here?

**Answer:**

Default (autonomous run): yes — sidebar tags render as plain text links with their count, and tags with 0 records are left out of the sidebar only (the tag tree page and tag pages keep every dictionary tag). Small, found by the requested prototype comparison, and the brief's typography rule is explicit.

## C5 — phone Recently updated — answered

**Asked:** 2026-10-16 — intake

**Question:** At 390px a Recently-updated row squeezes the title between the 96px ref and the nowrap date into a ~130px column. Fix shape?

**Answer:**

Default (autonomous run): below the existing 760px breakpoint the row wraps — ref and title on the first line, the date on its own line under the title, left-aligned. CSS only.

## C6 — the Russian visual fixture — answered

**Asked:** 2026-10-16 — intake

**Question:** The site language comes from the attached project's vault config, so `--root swarmlight=…` from this repo renders English chrome. Which Russian fixture for the visual check?

**Answer:**

Default (autonomous run): the swarmlight vault beside the brief (`/tmp/claude-1000/-home-anton-Dev--A-hermes-pet/36dbf90d-0102-4f43-add1-4a69775c2e2f/scratchpad/site/swarmlight/vault`), copied into a temp project `/tmp/specs-site-ru/` with a `.booping` marker (`vault_path: ./vault`, `latest_migration: 9999`) and a `vault/config.yaml` setting `core.specs.site.lang: ru` and the `mechanic` type labels, the same shape as `booping-python/e2e/cases/specs/site-renders-russian-labels-and-a-tier-own-type.txtar`; rendered with `bin/booping specs site` from that directory. When that swarmlight path no longer exists, the temp project is built from the fixture files of that txtar case instead (`-- fixtures/cwd/… --` sections). The temp project is the runner's, never committed.
