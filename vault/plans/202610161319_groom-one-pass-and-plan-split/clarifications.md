# Clarifications

Autonomous run (owner unavailable): every question below was settled by the run with a default and is recorded here instead of being asked.

## C1 — where the one-file draft lives — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** The draft is one file, but `index.md` already exists with hook-written frontmatter, and a failing contract check or a change request at the approval gate must return to the draft. Where is the draft written?

**Options:**

- `{plan-dir}/draft.md`, kept as groom's drafting source; split writes `index.md`'s body and the milestone files from it
- straight into `index.md`, split in place
- a scratch path outside the vault

**Answer:**

`{plan-dir}/draft.md`, body only, no frontmatter — `index.md` keeps owning the frontmatter (scaffold, hooks, `frontmatter-update`). A re-split after a fix runs with `--replace`. An in-place split leaves nothing to return to; a scratch path loses the draft from the vault's history (value/0004). After `ready-for-dev` develop never reads `draft.md`; it stays as the record of what groom drafted.

## C2 — research-web and research-codebase steps — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** V3a has one research stage over the code and no web-research stage. Do `research-codebase` and `research-web` survive as steps?

**Answer:**

Both step directories are deleted; the research stage over the code lives inside `draft-plan` (adr/0030: "one drafting pass … two stages, research then draft"). Checking external references was among the 16 rules the ablation found the model follows unprompted (`ext_verified`), so no separate web step. The `researching` status stays, now covering draft-plan's research stage.

## C3 — cross-review step — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** "No self-review step" — does that remove `cross-review`?

**Answer:**

No. `cross-review` is a config-gated second-model review (adr/0016), not the drafter reviewing itself; it stays as is. What goes is the self-review stage (V3's stage 3) and the instruction to walk the template's Quality Checklist item by item before returning.

## C4 — state machine wording — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** The request keeps groom's state machine. The `researching → drafting` and `drafting → cross-reviewing` edges name the deleted steps and the checklist walk. Change them?

**Answer:**

Statuses, edges and hooks stay identical; only the `when` and `gates` prose of those two edges changes — research done means draft-plan's research stage posted its facts, and leaving drafting means `booping plan split` exited 0 and `booping plan check` passed.

## C5 — exit codes of plan split and plan check — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** The request fixes exit 3 for "no milestone headings". What are the other codes, and how does a flag reach the driver?

**Answer:**

`plan split`: 0 written clean; 3 no milestone headings, nothing written; 4 written with flags (each flag a `flag:` line on stderr); 2 refused — milestone files already exist and `--replace` is not given, or a write failed; 1 usage or config error. `plan check`: 0 clean; 1 findings (one `{milestone dir}: {check}: {finding}` line each on stdout); 2 no plan or no milestone files. budget already owns 3/4 as named per-command constants, so local constants follow that precedent.

## C6 — SP groups rule — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** The prototype packs groups in dependency order; adr/0022 says graph order within one topological wave; develop's provision packs contiguous runs in `id` order. Which rule does `## Groups` follow?

**Answer:**

Develop's: contiguous runs in `id` order while the summed `sp` stays at or under `core.sprint.max_sp`; a single milestone is always a valid group; `max_sp: null` puts each milestone in its own group. A `depends_on` pointing at a later milestone is a flag. One rule in code and in develop's prose, so `## Groups` never disagrees with what develop briefs. Develop keeps computing its own groups — reading `## Groups` from develop is a later change.

## C7 — Sonnet fallback and the driver-owns-the-vault rule — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** adr/0031 sends a flagged plan to a Sonnet split; rule/0019 keeps every vault write with the driver. How does the fallback write?

**Answer:**

The fallback agent (model and effort from the new key `core.groom_playbook.split_fallback_agent`, default `sonnet:medium`) rewrites the draft into the fixed heading format at a scratch path under `/tmp`, writing nothing in the vault, and returns that path. The driver copies it over `draft.md` and re-runs `booping plan split --replace`, so the script stays the only writer of the milestone layout and the cut stays byte for byte. Departure from adr/0031's "Sonnet writes the files", taken to keep rule/0019.

## C8 — what the contract check checks — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** The request names three checks — one Verify command, named files, DoD per task. How are they measured, and does anything else belong in the check?

**Answer:**

Per milestone file: `verify` — `## Verify` holds exactly one command: one fenced block with one non-blank line, or one line that is a single inline code span; `files` — `## Tasks` names at least one path (a backticked token holding `/` or a file extension); `dod` — `## Definition of Done` has at least as many checkbox items as `## Tasks` has tasks (rows of a table whose header has a `Task` column, else top-level list items), and a milestone with no tasks is a finding; `sp` — `sp` is set and below `core.sprint.redecompose_threshold`, which moves the drafting gate that already exists in `playbook.yaml` into code (value/0015). The other milestone_contract prose (one procedure, deliverables as paths) has no reliable mechanical test and leaves with the partial — the ablation found the model keeps it unprompted (`no_two_ways`).

## C9 — contract fix loop bound — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** A failing milestone returns to the draft. How many rounds before the run moves on?

**Answer:**

Three split-and-check rounds. Findings still standing after the third are listed in present's summary as a check outcome, and the plan goes to the review gate with them.

## C10 — the 16 cut rules beyond backend.md — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** The ablation ran on `backend.md`. Are the cut rules dropped from the other four templates too?

**Answer:**

Yes: the same rules, matched by meaning, leave all five core templates, with the whole anti-pattern list. The milestone-shape items that moved into `booping plan check` leave the checklists too (adr/0030: "not repeated in the prompt"). The `# Quality Checklist` top-level section stays, so user-authored templates keep a valid shape; groom reads it as part of the template and no longer walks it as a separate pass.

## C11 — where the one-file milestone format is stated — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** adr/0030 says the template states the format split cuts on. Five core templates plus any user template would each carry it.

**Answer:**

The heading format is stated once, in `draft-plan`'s body, rendered from a new config key `core.groom_playbook.split.sections` (the four sub-heading names split writes), so user templates with the old "Milestone files" section still draft in the right format (value/0003, rule/0017). Each core template's milestone section keeps only what a milestone holds for its surface, as the content of those sub-headings.

## C12 — snapshot acceptance — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** rule/0013 says a run never accepts snapshot baselines.

**Answer:**

The owner's standing permission for this feature (2026-10-14) overrides it for this plan only: develop runs `just snapshots-accept groom` when every drifted hunk of `playbooks/groom/_reports/output.md` is a change this plan describes, and lists the report and why in `develop-defaults.md`. Any other drift stops the run. Only groom's report includes the touched partials.

## C13 — e2e fixtures from the benchmark plans — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** Which of the 12 benchmark plans become fixtures, and how are client data kept out?

**Answer:**

Four: one per benchmark task plus one second shape — `m2-V3a-r1`, `m2-V3-r2`, `s1-V3a-r1`, `c1-V3a-r1` from `~/Dev/@A/booping-benchmarks/groom/split/plans.txt`. Before copying, each is grepped for tokens, keys, emails, hostnames and internal URLs; a plan that carries any is replaced by the next plan of the same task, never redacted by hand (a redacted plan no longer tests the real shape). The fixture holds only the draft file.
