# Framing brief

## Request

> groom 1. use positional argument to set file. 2. It should work for cases like develop/groom/retro which all keep state on one index.md plan file. 3. Exmpicit

Raised while reviewing the freshly migrated `retro` playbook, where `intake` drops sibling plans with `booping transition done <plan>` while everything else in the run moves through `booping playbook-transition` — two writers for what reads as one kind of move. The preceding exchange established that `playbook-transition` resolves its target as `workdir / machine.artifact` with `{instance}` interpolated, and has no way to be pointed at a file directly.

## Task type

`feature` — a new CLI surface on `booping playbook-transition`: an argument that does not exist today, changing what the command can be asked to do.

- Not `bug`: nothing diverges from specified behaviour. The workdir-relative resolution works exactly as designed and documented in `CLAUDE.md`; the request is for a capability it never had.
- Not `refactoring`: the change is user-visible by definition — a new positional argument in the command's signature and a new resolution path for the artifact. A refactoring would leave the CLI contract untouched.

## Problem

`booping playbook-transition <playbook> <to> [--state] [--instance] [--workdir]` resolves the artifact it mutates as `workdir / machine.artifact`, with `{instance}` interpolated into the path first (`booping-python/src/booping/commands/playbook_transition.py::_resolve_artifact`). The file is therefore always addressed indirectly, through the machine's declared relative path plus a directory.

For `develop`, `groom` and `retro` that indirection buys nothing: all three keep run state on a single `index.md` that *is* the plan file, and the workdir is exactly that plan's own directory. The caller already knows the file it means; it has to decompose it into a directory and trust the manifest to name the leaf.

Where the indirection actively blocks work is any move against a file the machine's path does not describe. Retro hits this concretely: a sibling plan the user drops at intake lives at `{vault}/plans/{other-slug}/index.md`, outside the run workdir, so the only way to move it is `booping transition done <plan>` — the plan-lifecycle writer — leaving one run with two state writers and two different report formats.

The change: `playbook-transition` takes the artifact file as an explicit positional argument, addressing it directly rather than deriving it.

## Clarifications and Decisions

- The positional argument **replaces** `--workdir` rather than coexisting with it — one way to name the target, not two.
- It **overrides** the machine's declared path; where a path must vary, it is composed in the manifest through Jinja rather than by a second CLI flag.
- `booping playbook-state` takes the same positional treatment — the read side stays symmetric with the write side.
- Retro's own reframe, taken as a decision here because it motivates the shape: **the status belongs to the plan; `retro.md` is the run's output, not its state file.** A multi-plan run is therefore several transition calls, one per plan, each plan carrying its own `retro.md`.
- The `states:` key `artifact:` is renamed in the same plan — it reads as "the thing this run produces" when it means "the file this machine's `status:` lives on". The rename covers the manifest schema, `render-playbook`'s `## State` section wording, `playbook-state`'s output, the core playbook manifests and the docs.
- Boundary: this plan is **CLI + schema only**. Retro's playbook redesign — per-plan `retro.md`, siblings unified onto the new call, `close-working-set` retired, the goal-verdict stamp settled — is a separate plan groomed after this lands, since it is playbook design and depends on this CLI existing.
- One constraint carried forward for that later plan: hook strings are static, so the per-plan goal verdict (`success|partial|fail`) still cannot be a `frontmatter-update` value. A per-plan `retro.md` does make the reference stamp static (`retro=retro.md`), which a shared retrospective could not.
- No manual prose-shape reshape expected after implementation.

## Scope questions

1. **Does the positional replace `--workdir`, or coexist with it?** `--workdir` is not only the artifact anchor: `frontmatter-update <file> ...` hooks resolve their file targets against it, and hook scripts receive it as `BOOPING_WORKDIR` with cwd set to it. Options: (a) positional replaces `--workdir` entirely and the workdir becomes the artifact's parent directory — clean, but breaks any machine whose artifact sits in a subdirectory of the workdir (`playbook-authoring`'s `_specs/index.md`, `_specs/steps/{instance}/index.md`); (b) both accepted, positional overrides the artifact path only and `--workdir` keeps its hook role, defaulting to the artifact's parent when omitted.

2. **Does the positional override the machine's declared `artifact:`, or is it required to agree with it?** Overriding is what makes the retro sibling case work — the whole point is moving a file the manifest does not name. The cost is that reachability is then checked against a machine the target file may not belong to: nothing stops `playbook-transition retro awaiting-learning some-unrelated-file.md` from stamping a file that was never in the run.

3. **Same treatment for `booping playbook-state`?** It has the identical `--workdir` + `{instance}` resolution and is the read-side pair of this command. Symmetry argues yes; scope argues it can follow later.

4. **Does this land the retro unification, or is that a separate plan?** With an explicit target, retro's dropped and adopted siblings could both move through `playbook-transition` against a `sibling` machine, retiring `booping transition done <plan>` from the run and possibly the `close-working-set` script with it. That is a design change to the `retro` playbook, not to the CLI — it can ride along or be groomed on its own.

5. **Post-implementation reshape?** This is CLI + docs work, not prompt-shaped, so I do not expect a manual prose-shape pass after implementation — but `CLAUDE.md`'s CLI section and the playbook-driving partial both document the current invocation and will need rewording. Confirm whether you expect to reshape those by hand afterwards.
