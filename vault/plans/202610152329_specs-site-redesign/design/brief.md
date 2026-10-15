# Specs site redesign — brief (orchestrator, 2026-10-15)

Base spec: specs-site-design.md beside this file (from the swarmlight session: audit of 12 problems, users/tasks, skeleton, pages, search, machine layer, theme, priorities). Follow it, with the owner's corrections below, which win where they differ.

## Owner's words (verbatim, Russian)
«С сайтом — проблема в том, что он с точки зрения сценариев использования плохо продуман — это по сути представление документации, а тут вверху какая-то таблица, цифры мелкие куда кликать, лишний клик зачем не ясно. Посмотри на UX гайды и практики таких систем, сделай хорошую типографику для чтения документации и тд. Навигацию продумай, может clarify — просто фильтром сделать и иконкой на файле или иконки статуса добавить и тд. … по мобилке тоже хочу что-то продуманное.»

## Corrections to the base spec
- Home is a documentation landing, not a numbers dashboard: one framing line (project title + its first value's summary), the types as named reading scenarios with one-line meaning («Values — why the project exists», «Rules — what constrains decisions», «Decisions — why it was decided so» …, labels localised), recently updated. "Needs you" is ONE link/badge (e.g. «7 need you →») that opens the review filter — no grid of count cards, no count table.
- Review is a filter over the list, not a separate dashboard: chips "unreviewed", "has [clarify]", "has [unknown]", "open conflicts", "proposed ADRs", "open ideas/items"; each row says why it is listed (icon) and links straight to the mark's anchor in the record.
- Every record shows its state as icons + text: status badge, [clarify] (question icon + count), [unknown] (warning icon), unreviewed (hollow dot) — in lists, in the record header, in the sidebar. Inline SVG sprite (`<symbol>` + `<use>`), never colour alone, never emoji.
- Search: the base spec's own ~80-line vanilla search (Cyrillic-aware: lowercase, ё→е, crude stem, weights), loaded via `<script src>` so file:// works — NOT Pagefind/lunr (they need a build step or WASM).

## Typography (reading-first)
- Fonts are SHIPPED with the site, never `system-ui` (on the owner's Linux `system-ui` resolves to a monospace face and the whole site rendered mono): bundle Golos Text (OFL, Cyrillic-first; weights 400/500/600/700) for text and JetBrains Mono (OFL; 400/500) for refs and code as woff2 files in the site output, `@font-face` with `font-display: swap`; fallbacks `"Segoe UI", Roboto, "Noto Sans", Arial, sans-serif` and `"SF Mono", Consolas, monospace`. Monospace only for record refs and code.
- Body 17px / line-height 1.6, measure max 68–70ch; H1 28/1.3, H2 22/1.35, H3 18/1.4; meta/chips 13/1.4; code 15/1.5. 4px spacing unit; paragraph gap 1em, section gap 2.5em.
- Light: bg #ffffff, text #1a1a1a, secondary #5a5a5a, link #1b5fae, border #e2e2e2. Dark: bg #16181c, text #e4e6eb, secondary #9aa0a6, link #7fb0ff, border #2c2f36 (all ≥4.5:1; body ≥7:1 in dark). auto/light/dark toggle, no flash.

## Mobile
- Header: title + search icon (full-screen search overlay) + menu (drawer with the type tree, tags, review filter). Tap targets ≥44px. Breadcrumb shows the last level only.
- Lists become cards (title, summary, icon row). ADR alternatives table becomes one card per option (option, status, complexity, reversibility, verdict), chosen option first and open, others collapsed.
- On-page ToC and "open questions" collapse into `<details>` under the title. No horizontal scroll anywhere.

## Approved look
- The owner reviewed a clickable prototype and approved it: `specs-site-mockup.html` beside this brief (published as an artifact). Match its layout, spacing, palette tokens, badges, icons (SVG `<symbol>` set in it), chips, record page, ADR option cards and phone behaviour; it is the visual reference, not code to copy verbatim.

## Process
- Port, don't reinvent, from /home/anton/Dev/@A/shatterlings/crates/specs/src/site.rs (review page, tag tree, backlinks by section, superseded-by, llms, not_found, filter.js, mobile nav).
- `booping specs site-index` (from the Pages plan) follows the same design.
- Deterministic output; txtar/unit tests for data (filters, backlinks, superseded-by, search index, labels); a visual check: render booping's own vault records and swarmlight-like Russian fixtures, screenshot desktop and 390px mobile with a headless browser if available, and look at them.
