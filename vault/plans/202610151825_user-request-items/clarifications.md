# Clarifications

## C1 — source vocabulary — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** adr/0028 gives items a source (user request, spec gap, backlog task), but `source` already exists as a closed set of filing mechanisms (`manual`, `adr`, `mark`, `check`, `sync`, `correction`). One field or two?

**Options:**
- extend `source` with `request` and `backlog`
- a second field `kind` beside `source`

**Answer:** Default (autonomous run): extend the one `source` field with `request` and `backlog`. Every existing value is a way a spec gap is found, so the spec-gap category is those values; a second field would restate it (value/0003).

## C2 — command surface — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** `booping items add` beside `booping specs open-items add`, or one group?

**Answer:** Default (autonomous run): one top-level group `booping items` with every verb (`add`, `list`, `plan`, `close`, `reopen`, `scan`); `booping specs open-items` is removed and every reference — playbook prompts, the `open-items-follow-plan` script, eval fixtures, docs, CLAUDE.md, e2e cases — is cleaned in this sprint (rule/0007). Two command paths into one store would drift (value/0003); the group never shipped in a tag, so nobody calls it yet.

## C3 — verbatim text input — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** How does a channel pass the user's words so they land verbatim?

**Answer:** Default (autonomous run): `--text TEXT`, or `--text -` to read stdin; the text is the item body under the H1, byte-for-byte (no escaping, no Jinja evaluation of `{{`, inner newlines and trailing whitespace kept). `--body` is replaced by `--text`.

## C4 — direction on a request — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** A user request has no spec direction. Required, defaulted or null?

**Answer:** Default (autonomous run): `direction` stays required for the spec-gap sources and is `null` for `request` and `backlog`; giving one for those sources is an error.

## C5 — title of a request — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** A messenger bridge may have no title. Required?

**Answer:** Default (autonomous run): optional for `request`/`backlog`; absent, it is the text's first sentence, truncated — the existing `first_sentence` and `truncate` helpers.

## C6 — concurrent ids — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** `next_id` is an unlocked max+1; several channels may add at once.

**Answer:** Default (autonomous run): the item file is created with an exclusive create; a taken id moves to the next one and retries. No lock file.

## C7 — index columns — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** Should `booping items list` show where an item came from?

**Answer:** Default (autonomous run): yes — `source` joins the index columns after `status`.

## C8 — config, directory, ids, machine — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** Move `core.specs.open_items` to a shared key, rename the directory or ids?

**Answer:** Default (autonomous run): no. They stay as they are; every change is additive to item files, so no vault migration ships. Relocating the config key is the project-manager's call when it lands.

## C9 — scope boundary — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** What of adr/0028's item surface lands here?

**Answer:** Default (autonomous run): only the model and `booping items add`. Out: splitting one message into several items and questions on the item (part 4, the project-manager playbook), a channel field, intake bridges, duplicate merging and trackers (adr/0028, not core).

## C10 — plan approval — answered

**Asked:** 2026-10-15 — groom/present

**Question:** The plan is ready for development — approve, or say what to change?

**Answer:** Default (autonomous run): approved as written — 15 SP, under the 35 SP split threshold, so no split; the cross-review (codex) returned no findings. No plan branch: the run stays on `feat/specs` as directed.
