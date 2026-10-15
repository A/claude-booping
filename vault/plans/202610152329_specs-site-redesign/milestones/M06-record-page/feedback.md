# Feedback

**Blocked (1/2)**: markup classes the milestone renders have no styles

- Checked: `style.css` against the classes the new templates emit and the mockup's stylesheet (`../../design/specs-site-mockup.html`, `<style>` block, light and the 760px phone block).
- Wrong: the templates emit `.lead`-adjacent head parts and lists that `style.css` never styles — `.tags`/`.tag`, `.facts` (dt/dd grid), `.relations` and `ul.rel` (`.rel li`, `.rel .ref`), `ul.rows`/`.row` (`.t`, `.s`, `.why`, `.ref`, hover), `.types`. Type and root lists show browser bullets and indentation; the record head and facts are unstyled. M03 promised the mockup's layout classes; these were missed.
- Next attempt: port the mockup's rules for these classes into `booping-python/src/booping/specs/site/style.css` using the existing tokens — desktop and the single 760px block (rows stacked, facts one column, tap targets ≥ 44px) — with `ul.rows`, `ul.rel`, `.types` list-style and padding reset. Add a `site_pages_test.py`/`site_contrast_test.py` assertion that every class the templates emit for rows, tags, facts, relations and types has a rule in `style.css`. Keep `site_contrast_test.py` green. Change no template markup and no goldens unless a golden embeds `style.css`.
