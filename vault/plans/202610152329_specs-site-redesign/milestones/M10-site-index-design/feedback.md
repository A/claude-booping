# Feedback

**Blocked (1/2)**: project rows mis-laid on desktop

- Checked: the site-index rows against the shared `.row` grid in `booping-python/src/booping/specs/site/style.css` (`96px minmax(0,1fr) auto`, built for record rows that start with a ref).
- Wrong: a project row has no ref, so on desktop the project name sits in the 96px ref column and the description in column 2.
- Next attempt: add a ref-less row variant in `style.css` (a class on the site-index rows, set in `site_index.html.j2`) so the name takes the main column and the description sits under or beside it as in the mockup's rows; phone layout unchanged. Rebaseline only the site-index goldens whose markup changes, read their diffs, and keep `uv run pytest e2e -k site-index -q` and `tests/specs -k site` green.
