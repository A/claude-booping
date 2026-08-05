---
status: spec-ing
---

# setup-booping

[← index](../../index.md)

## Contract

- **Needs** —
  - whether booping is initialized on this machine — the booping-initialized flag from the
    run's context report (the flag is an assumed prerequisite: it does not ship yet, and the
    step is written against it landing in the rendered project-context report)
  - the machine's configured home dir, when there is one
  - the user's preferred home dir, asked in-step with `AskUserQuestion` and defaulting to
    `~/Claude/`, only when booping is not yet initialized
- **Value** — the machine level settled before any project work touches it: a booping config
  exists and its `home_dir` is resolved and reported, either because it already was — in which
  case nothing on the machine changes — or because the user picked one and the step created the
  config. The resolved value is what the project level scaffolds under, so the run never guesses
  it. Reading it back is `booping config-get home_dir`, which resolves the merged core → global
  tiers and prints the raw unexpanded value; it always prints something (the core default
  `~/Claude/`), so it answers *what* the home dir is, never *whether* one is configured — that
  question is the context-report flag's alone.
- **Output files** —
  - `[CREATED] ${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml` — the machine (global) config
    tier, holding a single `home_dir:` key set to the user's answer. Written **only** when
    booping is not yet initialized; when it is, the step writes nothing at all and never edits,
    re-points or reformats the existing file.
- **Harness return** — `## Changed:` carrying the config path when one was created and empty
  otherwise; `## Notes:` reporting the resolved `home_dir` and which branch produced it.
- **Review gate** —
  - none — the home-dir choice is taken in-step via `AskUserQuestion`
- **Delegation** — inline: the runner performs the step. Model tier recorded for it:
  `sonnet-5:medium`.

## Example artifact

Created only on the not-yet-initialized branch — `${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml`:

```yaml
home_dir: ~/Claude/
```

On the already-initialized branch there is no artifact: the step reports the resolved home dir
and leaves the machine untouched.

## Return Format

Booping was not initialized — the user chose a home dir and the config was created:

```markdown
## Changed:
- [CREATED] ~/.config/booping/config.yaml

## Notes:
- home_dir: ~/Claude/ (created)
```

Booping was already initialized — nothing written:

```markdown
## Changed:

## Notes:
- home_dir: ~/Work/claude/ (already configured, unchanged)
```
