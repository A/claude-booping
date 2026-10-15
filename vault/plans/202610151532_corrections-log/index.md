---
title: "Corrections log — booping correction add, the corrections sidecar, retro's
  feed"
type: "feature"
status: in-progress
sp: 20
related_to: null
created: 2026-10-15 15:32
planned: null
started: 2026-10-15 15:47
completed: null
code_reviews: []
sessions:
- 6a68e361-5db5-43f6-9580-ac2e1ae7254d
- 472924ad-8031-4e2b-b103-b50d62cb8074
retro: null
summary: booping correction add logs user corrections with a dialogue link into 
  a corrections.md sidecar; core rule; retro reads the feed
commit: 202b1dab393736e6f8b6e2564a654b4e5235b9c9
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents: '{"research-codebase": "a532951ede0d0389c", "cross-review": "a67b2e29dfcbaa692"}'
reviewed_at: 2026-10-15 15:46
---

# Corrections log — booping correction add, the corrections sidecar, retro's feed

## Context

Retro today finds the moments the user corrected the model by mining whole session transcripts over the plan's time window (`playbooks/retro/prepare/base.md`, brief A) — costly in tokens and lossy over long sessions. Nothing records a correction when it happens. [adr/0026](../../specs/adr/0026-corrections-log.md) decides to log them as they happen.

After this plan:

- `booping correction add` appends one entry — step, did, said verbatim, why, a dialogue link (session id + jsonl line + message uuid, found the way `session-stats` finds the transcript) — to `corrections.md` beside the run artefact: the plan's `index.md` for groom and develop, the review record for code-review. With `--record` it also files an open item (`source: correction`), per adr/0026's first consequence.
- `booping correction list --plan` prints every correction logged against a plan — its own sidecar plus those of its code reviews.
- A core rule, `booping:rule/0031`, targeted at `groom`, `develop` and `code-review`, tells the driver to log each correction.
- Retro's `prepare` step reads the feed first and hands its dialogue links to session-log mining.

Goal (feature guidance): retro starts from a ready list of corrections with links back into the dialogue, instead of digging them out of transcripts.

### Values in play

Per [booping:rule/0030](../../../specs/rule/0030-planning-shows-values-in-play.md):

- [value/0015](../../specs/value/0015-deterministic-where-it-can-be.md) deterministic — the entry format, numbering, sidecar placement, transcript lookup, the dialogue position and the plan's feed are CLI code with e2e cases; the model spends tokens only on noticing a correction and saying what it did.
- [value/0001](../../specs/value/0001-curated-self-learning.md) curated self-learning — a correction is logged, not turned into a rule; it reaches a rule only through retro and learn with the user.
- [value/0004](../../specs/value/0004-analysable-history.md) analysable history — the sidecar is plain markdown in the vault beside the artefact, with a stable shape and a link back to the dialogue.
- [value/0002](../../specs/value/0002-minimal-effective-context.md) minimal context — the rule reaches the three playbooks as a one-line brief; the format lives in `docs/corrections.md`, linked from the rule record, and the CLI is its only writer.
- [value/0003](../../specs/value/0003-single-source.md) single source — the `said` quote is checked against the transcript, never paraphrased; the open item a correction files links back to the entry instead of copying it.

### Departures

- **No transcript is a warning, not an error** (stretches value/0015's "computed by code"): `CLAUDE_CODE_SESSION_ID` is undocumented, so with no session id or no transcript the entry is still written with `**Dialogue:** not found — {reason}` and a stderr warning, exit 0 — the stamp-session precedent. A transcript that is found but holds no user message containing `said` is exit 1, so the quote stays verbatim. See C4.
- **Snapshot reports are accepted inside the run** (departs from [rule/0013](../../specs/rule/0013-snapshot-baselines-accepted-by-user.md)): the owner's standing permission for this feature (2026-10-14) allows `just snapshots-accept` when every drifted hunk is one this plan describes; develop lists each accepted report in `develop-defaults.md`.
- **Retro keeps session-log mining** (adr/0026 rejected "mine the transcripts at retro" as retro's feed, not as a second pass): the feed comes first and mining still looks for the tensions and detours a correction log does not hold, starting from the feed's dialogue links. See C6.

## Decisions

- **Scope**: part 3 of the request only; part 4 (autonomy modes) stays parked — C1.
- **Sidecar placement**: `{dirname(--target)}/corrections.md` — the plan directory for groom and develop; `codereviews/{dir}/corrections.md` for code-review, shared by that directory's reviews, each entry naming its artefact — C2.
- **CLI surface**: a top-level `correction` command with verbs `add` and `list` — C3.
- **Dialogue link**: session id from `--session`, else `CLAUDE_CODE_SESSION_ID`; transcript via `session_stats.locate_transcript` under `~/.claude/projects`; position = the 1-based jsonl line and `uuid` of the last user message containing `said` (whitespace-normalised) — C4.
- **Open item from a correction**: `--record REF` files `open-items add --direction conflict --source correction --record REF`, `correction` added to the `source` set — C5.
- **Retro feed**: `prepare` runs `booping correction list --plan` per plan in the working set; each entry becomes an issue item with source `correction`; learn is unchanged, it reads the retrospective — C6.
- **The rule**: `specs/rule/0031-corrections-are-logged.md`, core tier, `targets: [groom, develop, code-review]` — playbook-level, so every step of the three — C7.

## Architecture

```
groom / develop / code-review driver ── booping:rule/0031 brief (## Rules) ──▶ notices a correction
        │
        ▼
booping correction add --target {artefact} --step … --did … --said … [--why …] [--record REF]
        │  sidecar = dirname(target)/corrections.md, next R{n}
        │  CLAUDE_CODE_SESSION_ID / --session ──▶ session_stats.locate_transcript ──▶ line + uuid of the user message holding `said`
        │  --record ──▶ open_items.add(source=correction, direction=conflict) ──▶ open-items/OI-NNNN.md
        ▼
plans/{slug}/corrections.md   codereviews/{dir}/corrections.md
        ▲                              ▲ (via the plan's code_reviews: list)
booping correction list --plan plans/{slug}/index.md
        ▲
retro prepare ──▶ issue items (source: correction) + dialogue links into brief A (session-log mining)
```

### corrections.md

Plain markdown, no frontmatter, seeded with `# Corrections` on the first `add`. One H2 per entry, in the order logged:

```markdown
# Corrections

## R1 — groom/draft-plan — 2026-10-15 15:40

**Did:** proposed one plan over the 35 SP threshold

**Said:**

> split it, corrections first

**Why:** not stated

**Dialogue:** `6a68e361-5db5-43f6-9580-ac2e1ae7254d` line 212 · `4f2c9a1e-0b7d-4c55-9e0a-6d1f3b2a8c90`

**Record:** value/0007 → [OI-0004](../../open-items/OI-0004.md)

**Artifact:** [index.md](index.md)
```

- `R{n}` numbered from `R1` across the file, next = highest + 1, never reused.
- Heading: id, `--step` verbatim, the local date and time (`core.macros.date`, `+%Y-%m-%d %H:%M`).
- `**Said:**` — every line of `--said` prefixed `> `, never reworded.
- `**Why:**` — `--why`, or `not stated` without it.
- `**Dialogue:**` — `` `{session}` line {n} · `{uuid}` ``; without a session id or a transcript: `not found — no session id` | `not found — no transcript for {session}`.
- `**Record:**` — only with `--record`: the ref, an arrow and a link to the filed item, relative to the sidecar.
- `**Artifact:**` — a link to `--target`, relative to the sidecar.

### Transcript match

A *user message* is a jsonl record with `type: user`, not `isMeta`, not `isSidechain`; its text is the string `message.content`, or the concatenated `text` blocks and `tool_result` contents of an array (so a gate answered through `AskUserQuestion` matches too). Both the text and `--said` are whitespace-normalised — split on any Unicode whitespace and rejoined with one space (Python `' '.join(s.split())`); the match is a substring test; the last matching record wins.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [booping correction add writes the corrections sidecar](milestones/M01-correction-add-writes-the-sidecar/M01-correction-add-writes-the-sidecar.md) | 4 | done |
| 02 | [add links the entry to the dialogue](milestones/M02-dialogue-link-from-the-transcript/M02-dialogue-link-from-the-transcript.md) | 4 | done |
| 03 | [add --record files an open item](milestones/M03-correction-files-an-open-item/M03-correction-files-an-open-item.md) | 3 | done |
| 04 | [booping correction list prints a plan's feed](milestones/M04-correction-list-for-a-plan/M04-correction-list-for-a-plan.md) | 3 | done |
| 05 | [Core rule 0031 and the corrections format doc](milestones/M05-corrections-rule-and-format-doc/M05-corrections-rule-and-format-doc.md) | 2 | pending |
| 06 | [Retro prepare reads the corrections feed](milestones/M06-retro-reads-the-feed/M06-retro-reads-the-feed.md) | 2 | pending |
| 07 | [Docs and CLAUDE.md name corrections](milestones/M07-docs-and-claude-md/M07-docs-and-claude-md.md) | 2 | pending |

## I/O contract

Run anywhere inside a booping project; paths printed vault-relative. Exit `0` success, `1` user error with one `error: …` line on stderr and nothing on stdout — same as `booping specs open-items`.

- `correction add --target PATH --step TEXT --did TEXT --said TEXT [--why TEXT] [--record REF] [--session ID]`
  - `--target` — vault-relative run artefact; must exist (`error: target not found: {path}`).
  - `--said` — non-empty; with a transcript found and no user message containing it: `error: --said is not verbatim in any user message of session {id}`, nothing written.
  - `--record` — `[{namespace}:]{type}/{NNNN}`, `{type}` one of the `core.specs.format` schema stems; existence is not checked (a cross-tier ref may not resolve on this machine). Anything else: `error: --record must be [namespace:]type/NNNN: {value}`.
  - `--session` — overrides `CLAUDE_CODE_SESSION_ID`.
  - stdout: `{sidecar}#R{n}` (e.g. `plans/x/corrections.md#R1`); with `--record`, a second line, the item path `open-items/OI-NNNN.md`.
  - stderr: `warning: no session id; dialogue not linked` | `warning: no transcript for {session}; dialogue not linked` on the exit-0 fallback.
- `correction list --plan PATH`
  - `--plan` — vault-relative plan `index.md`; must exist.
  - stdout: per existing sidecar — the plan's own first, then one per distinct directory of the plan's `code_reviews:` entries in list order — a line `# {sidecar path}`, a blank line, then the file's body below its H1. No sidecar: the single line `no corrections for {plan}`.

## Final Verification

- [ ] `booping correction --help`, `add --help` and `list --help` list the flags of the I/O contract.
- [ ] Happy path and every exit-1 path of the I/O contract are e2e cases under `booping-python/e2e/cases/correction/`.
- [ ] `bin/booping render-playbook groom`, `develop` and `code-review` each carry the `booping:rule/0031` brief in `## Rules`; `bin/booping render-playbook retro --step prepare` names `booping correction list`.
- [ ] `just snapshots` drifts only in groom's, develop's and code-review's reports (the injected rule) and retro's (prepare); each accepted per the run's snapshot policy.
- [ ] `just ci` is green.

## Risk register

- The rule relies on the driver noticing a correction (adr/0026's own con) — accepted; retro's session-log mining stays as the second net (C6).
- `CLAUDE_CODE_SESSION_ID` is undocumented and may disappear — mitigated by the warning fallback (C4) and `--session`.
- The verbatim check may reject a quote the harness reshaped (pasted-content tags, attachments) — mitigated by whitespace normalisation and substring matching: the agent quotes the part it can copy exactly.
- Two concurrent `correction add` calls on one sidecar could race on `R{n}` — accepted: one driver logs per run, and value/0011 already trades concurrent writes away; every validation runs before the single write, so an error leaves the file untouched.
- A shared `codereviews/{dir}/corrections.md` mixes several reviews' entries — mitigated by `**Artifact:**` on every entry.

## Out of scope

Parked sibling stub, groomed in its own run:

- **Autonomy modes** ([adr/0027](../../specs/adr/0027-autonomy-modes.md)) — a project config key `supervised` (default) | `autonomous`; the specs playbook's open-items scenario and a manager path ([adr/0028](../../specs/adr/0028-one-project-manager.md)) honour it (autonomous: groom + develop without stopping, gates auto-confirmed, defaults recorded); uncommitted changes on a branch during a migration always shown and asked about, in either mode.

Also out: logging corrections in playbooks other than groom, develop and code-review; learn reading sidecars directly (it reads the retrospective); a correction verb to edit or delete an entry (the sidecar is plain markdown).

## CLAUDE.md impact

Owned by M07: `## Commands` `bin/booping` subcommand list gains `correction` (`add`, `list`); `## Lifecycle` gains a **Corrections** bullet (the `corrections.md` sidecar beside the run artefact, written only by `booping correction add`, format `docs/corrections.md`, read by retro's `prepare`).
