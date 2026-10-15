---
id: "03"
title: "Comment hooks in the generated HTML and the storage module"
sp: 4
status: pending
plan: "/home/anton/Dev/@A/claude-booping-specs/vault/plans/202610160336_specs-site-review-comments/index.md"
---

# M03: Comment hooks in the generated HTML and the storage module

Every page carries the static hooks the comment UI needs — record identity, the sidebar entry, the record header button, the dialog shells, the `comments.html` shell, the labels — and `comments.js` reads and writes the store and fills the sidebar count.

**Scope** (all under `booping-python/src/booping/specs/site/` unless rooted otherwise):

- `templates/record.html.j2` — the `article` gets `data-ref="{ref}" data-title="{title}" data-page="{record page path from the site root}"`; the page includes a new `templates/_comments.html.j2` partial holding two closed `<dialog>`s: `dialog.cmt-sheet` (heading "My comments", an empty `ul.cmt-list`, an empty-state line, buttons "Copy for the model" and "Clear sent", a close button) and `dialog.cmt-compose` (a `blockquote` preview, a labelled `textarea`, Save and Cancel). Every string the JS needs and the page does not already show sits on the dialogs as `data-*` attributes (plural forms as JSON, like `data-forms` in `templates/search.html.j2`).
- `templates/base.html.j2` — a header `button.iconbtn.cmt-open` (`i-comment` icon, aria-label "My comments", an empty `span.n`) rendered only on record pages (a block the record template fills); a sidebar `<li class="cmt-nav" hidden>` after "All records" linking `{prefix}comments.html` with label "My comments" and an empty `span.n`; `<script src="{prefix}comments-format.js" defer>` and `<script src="{prefix}comments.js" defer>` on every page; `data-prefix` stays the source of the site root.
- `templates/comments.html.j2` (new) + its `page(...)` call in `pages.py` — `comments.html` at the site root: h1 "My comments", lead "Stored in this browser only.", an empty `div.cmt-groups`, the Copy and Clear sent buttons, an empty-state line, a `p.needs-js` fallback, the same `_comments.html.j2` compose dialog. Copy `search.html.j2`'s shape.
- `templates/_icons.html.j2` — `i-comment` symbol (speech bubble, same viewBox and stroke style as the others).
- `src/config.yaml` — labels under `core.specs.site.labels.{en,ru}.ui`, exactly: `my_comments` "My comments" / «Мои комментарии»; `comment` "Comment" / «Комментировать»; `comment_section` "Comment on this section" / «Комментировать раздел»; `comment_paragraph` "Comment on paragraph" / «Комментировать абзац»; `comment_note` "Note" / «Заметка»; `save` "Save" / «Сохранить»; `cancel` "Cancel" / «Отмена»; `edit` "Edit" / «Изменить»; `delete` "Delete" / «Удалить»; `close` "Close" / «Закрыть» (reuse if one exists); `copy_for_model` "Copy for the model" / «Скопировать для модели»; `clear_sent` "Clear sent" / «Удалить отправленные»; `sent` "sent" / «отправлен»; `no_comments` "No comments yet." / «Комментариев пока нет.»; `comments_lead` "Stored in this browser only." / «Хранятся только в этом браузере.»; `comments_need_js` "Comments need JavaScript." / «Для комментариев нужен JavaScript.»; `comments_need_storage` "Comments need browser storage." / «Для комментариев нужно хранилище браузера.»; `comment_deleted` "Comment deleted" / «Комментарий удалён»; `copy_failed` "Copy failed" / «Не удалось скопировать»; plurals `comments_copied_n` ["{n} copied", "{n} copied"] / ["{n} скопирован", "{n} скопировано", "{n} скопировано"] and `comments_cleared_n` ["{n} cleared", "{n} cleared"] / ["{n} удалён", "{n} удалено", "{n} удалено"].
- `comments.js` (new, shipped by `pages.py` like `site.js`) — this milestone's part only: the store per `../../clarifications.md` C5 (key `specs-comments:v1:` + `new URL(prefix, location.href).href`, JSON array, every access in try/catch, `load()`/`save()`/`add()`/`update()`/`remove()` with `id` from time + random suffix), `html.cmt` class set when storage works, the sidebar `li.cmt-nav` unhidden with its count (shown when > 0), the record header button's count, and a `storage`-event refresh. M04 and M05 extend this file.
- `style.css` — `.cmt-nav`, `.cmt-open` count badge and every comment control hidden unless `html.js.cmt`.

Tests (integration, `booping-python/tests/specs/site_pages_test.py`): a record page's article carries the three `data-*` values hand-derived from the fixture (incl. a Cyrillic title escaped as HTML); a record page holds both dialogs closed and the header button; a non-record page has the sidebar entry and no `cmt-open`; `comments.html` exists with its shell; the `ru` labels resolve on a `lang: ru` fixture; `search-body.js`, `index.json` and `llms.txt` are unchanged by the new markup. Rebaseline the `site-*.txtar` goldens and read the diff: only the hooks above.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Templates: article data, header button, sidebar entry, dialogs partial, `comments.html`, icon; labels en/ru; tests; golden rebaseline. | `booping-python/src/booping/specs/site/templates/record.html.j2`, `booping-python/src/booping/specs/site/templates/base.html.j2`, `booping-python/src/booping/specs/site/templates/_comments.html.j2`, `booping-python/src/booping/specs/site/templates/comments.html.j2`, `booping-python/src/booping/specs/site/templates/_icons.html.j2`, `booping-python/src/booping/specs/site/pages.py`, `src/config.yaml`, `booping-python/tests/specs/site_pages_test.py`, `booping-python/e2e/cases/specs/site-*.txtar` | 3 | pending |
| 3.2 | `comments.js` store and counts; shipped; CSS gating. | `booping-python/src/booping/specs/site/comments.js`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/style.css` | 1 | pending |

## Definition of Done

### Task 3.1

- [ ] Every hook listed in Scope is in the generated HTML; labels exactly as listed, en and ru.
- [ ] The tests above pass with hand-derived values; two builds of one fixture are byte-identical (existing determinism test still green).
- [ ] `site-*.txtar` rebaselined with `just e2e -k site --txtar-update`; the diff shows only the listed hooks, script tags, `comments.html` and the shipped JS files.

### Task 3.2

- [ ] `comments.js` touches storage only inside try/catch; with storage throwing, no error reaches the console and `html.cmt` is not set.
- [ ] The sidebar entry shows with JS and storage, its count hidden at 0.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/templates/search.html.j2` — JS-populated page shell with `data-forms` and a `needs-js` fallback.
- `booping-python/src/booping/specs/site/site.js` — theme storage in try/catch, `#status` announce, the drawer's focus handling.
- `../../clarifications.md` — C4, C5.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py e2e -k site -q`
