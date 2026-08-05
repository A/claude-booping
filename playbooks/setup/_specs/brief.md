---
reviewed_at: 20260804 05:07
---

# setup — Brief

## Goal

Take a repo from any starting state to a working booping project, in one driven procedure. Two
levels: **setup booping** (machine level) discovers the booping config and its `home_dir` and,
when absent, asks the user for a preferred home dir (default `~/Claude/`) and creates the
config; **setup project** discovers the project vault and, when absent, asks where the vault
should live (inside the project repo, or under the booping home dir), how to name the project
(offering candidates derived from the repo directory name), and whether `.booping` in the repo
root should be gitignored (moot when the vault itself lives in the repo) — then scaffolds the
vault, writes the marker, and, when the vault lives in the repo, symlinks it into the home dir.
Detecting the repo's stack, seeding only those `_booping/` extension files that carry signal the
repo's own `CLAUDE.md` lacks, and seeding `sprints.md` carry over from the existing `/install`
skill. This is **informed by `/install`**, not a port of it: the machine-level config phase is
first-class here, and the repo-vault → home-dir symlink is new behaviour.

## Success result

The project is ready to operate — from whichever entry state the run started in: booping was
never set up on this machine, and/or this is a new project, and/or both. A booping config exists
with a resolved `home_dir`; a vault exists at the chosen location with its standard
directories; the repo carries a correct `.booping` marker (gitignored if the user asked for
that), and a repo-local vault is symlinked into the home dir; the justified subset of
`_booping/` extension files is seeded, with existing non-empty files preserved and a stack
mismatch surfaced rather than silently overwritten; `sprints.md` is seeded. Every phase already
satisfied on entry is detected and skipped rather than redone, so a re-run on a fully set-up
project reports the state instead of changing it. The user is shown what landed and the next
command to run; a cancelled run leaves the machine and the repo untouched.

## Artifact home

None — the run is ephemeral. The booping config, the scaffolded vault and the `.booping` marker
are the only artifacts; there is no run directory and no process files reviewed on disk.

## Wishes

- Ephemeral by design — the run lives in one conversation and is not resumable; no run state,
  no `_runs/` workdir, no on-disk process files.
- Two-level decomposition, machine before project: **setup booping** (config + `home_dir`
  discovery, else ask and create) then **setup project** (vault discovery, else ask and
  scaffold). Each level is discovery-first — ask only what is genuinely missing.
- The project-level questions, as sketched: vault location (project repo or booping home dir);
  project name (offer candidates derived from the project directory name); whether `.booping`
  in the repo root must be gitignored (meaningless, and so skipped, when the vault lives in the
  repo). Asked via `AskUserQuestion`.
- A repo-local vault gets symlinked into the booping home dir.
- Carry over from `/install`: stack detection from the repo's signal files, the justified
  `_booping/` extension seeding (write a file only when it carries project-local signal the
  repo `CLAUDE.md` lacks, and report each skip with its reason), and `sprints.md` seeding.
- Carry over `/install`'s hard rules as playbook-level rules: never overwrite an existing vault
  without confirmation, never write `.booping` without asking, never edit the attached repo's
  own `CLAUDE.md`.
- Keep the decision points as real review gates: the machine-level home dir before the config
  is created, the project-level answers before scaffolding, and the detected stack before
  extensions are seeded.
- Retiring or deleting the existing `/install` skill is out of scope for this playbook.
