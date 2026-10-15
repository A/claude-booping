---
id: "02"
title: "add links the entry to the dialogue"
sp: 4
status: done
plan: "plans/202610151532_corrections-log/index.md"
---

# M02: add links the entry to the dialogue

`booping correction add` links each entry to the user message holding `--said` — session id, jsonl line and `uuid` — or refuses a quote that is not verbatim.

**Scope**: `booping-python/src/booping/correction.py` — session id from `--session`, else env `CLAUDE_CODE_SESSION_ID`; transcript via `booping.session_stats.locate_transcript(session, default_projects_root())`; the user-message test and normalised substring match exactly as `index.md` `### Transcript match`; last match wins; `**Dialogue:**` as `index.md` `### corrections.md`. No session id or no transcript → the `not found — …` value and the stderr warning of `## I/O contract`, exit 0. Transcript found, no match → `error: --said is not verbatim in any user message of session {id}`, exit 1, nothing written. Reuse `session_stats`' reading helpers; do not add a second jsonl parser.

Tests: integration tier, txtar cases with a fixture transcript under `fixtures/home/.claude/projects/proj/{session}.jsonl` — a string-content user message matches with its line and uuid; a quote whose whitespace differs still matches; an `isMeta` and an `isSidechain` record holding the quote are skipped; a `tool_result` answer matches; two matching messages link the later one; `--session` overrides the env; a session with no transcript writes `not found — no transcript for {session}` with the warning; a quote absent from the transcript is exit 1 with no file written.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Session resolution, transcript lookup, user-message text extraction and the match. | `booping-python/src/booping/correction.py`, `booping-python/src/booping/session_stats.py` | 3 | done |
| 2.2 | The txtar cases named in Tests. | `booping-python/e2e/cases/correction/add-dialogue-*.txtar` | 1 | done |

## Definition of Done

### Task 2.1

- [x] `**Dialogue:**` carries the 1-based jsonl line and the `uuid` of the last matching user message.
- [x] Meta and sidechain records never match; `tool_result` text does.
- [x] Any change to `session_stats.py` leaves `just e2e -k session-stats` green.

### Task 2.2

- [x] One case per behaviour named in Tests; line numbers and uuids in `expected/` hand-counted from the fixture.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/session_stats.py` — `locate_transcript`, `default_projects_root`, `_is_real_prompt`, `_blocks`.
- `booping-python/e2e/cases/session-stats/a-session-with-no-transcript-warns-and-the-run-continues.txtar` — fixture transcript layout under `fixtures/home/.claude/projects/`.

## Verify

`just e2e -k "correction and dialogue"`
