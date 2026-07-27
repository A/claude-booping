---
name: research-codebase
title: Research Codebase
summary: "Owns the review-the-codebase craft rule (blast radius + prior art); returns a bounded map, never file dumps."
agent: booping:booping-researcher
review_gate: null
---
## Charge

Map the blast radius of the requested change in the attached repo, from the **Codebase unknowns** listed in the run-time context.

- Files, modules, and packages the change touches or reads.
- Integrations and external surfaces affected: HTTP endpoints, CLI commands, schemas, migrations, config keys, env vars, public exports, generated artefacts.
- Prior art: existing implementations of the same shape in this repo, and the conventions they follow (naming, layering, test style, error handling).
- Constraints already encoded in the repo: `CLAUDE.md` rules, lint/typecheck/test tooling, build steps that must be re-run.

Read only what you need to answer this. Do not propose a design, do not write code, do not edit any file.

## Return contract

Return **only** the sections below, ≤ 50 lines total. No preamble, no restatement of the brief, no closing summary.

- **Blast radius** — up to 15 entries, each `path[:symbol]` + one line on why it is touched.
- **Prior art** — up to 5 entries, each `path` + one line on the pattern to follow.
- **Conventions** — up to 5 one-line rules the plan must respect (including the build/test commands that must pass).
- **Risks / unknowns** — up to 5 one-line items, each naming what is uncertain and what would resolve it.

Never paste file contents beyond a 3-line excerpt, and only when the exact text is load-bearing. Omit a section entirely if it has nothing in it.
