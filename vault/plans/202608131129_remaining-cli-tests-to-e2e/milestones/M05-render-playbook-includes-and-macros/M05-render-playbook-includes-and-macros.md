---
id: "05"
title: "render-playbook include chain and macro stubs"
sp: 2
status: pending
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M05: render-playbook include chain and macro stubs

The Jinja loader chain a body's `{% include %}` resolves against, and the `--stub-macro` surface, are pinned by txtar cases.

**Scope**: `render-playbook` include resolution and macro execution. Files: new `booping-python/e2e/cases/render-playbook/*.txtar`. Ported from the `include search chain` and `stubbable macro()` sections of `tests/test_render_playbook.py` (lines 1076–1166, 1752–end) plus the Jinja macro-stamp case left by M04. The core tier of the chain cannot be planted from a fixture — `get_plugin_root()` resolves to the real repository — so the core case includes a shipped partial from `playbooks/_partials/` by its root-relative name and asserts a line of that partial's own text.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Include-chain cases: a bare name resolving from the step directory and from the playbook directory, a root-relative name resolving from the playbook root, a relative include resolving against its including file, a later-wave step's fetched body resolving a playbook-dir include, local-over-global precedence, global fallback, core fallback against a shipped partial, and a missing include as a blocking notice | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | pending |
| 5.2 | Macro cases: `--stub-macro` reaching a playbook body and a Jinja preamble stamp, an unstubbed macro genuinely executing, and a stubbed value landing in a `--step` render too | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | pending |

## Definition of Done

### Task 5.1

- [ ] Six cases cover the chain positions — step dir, playbook dir, playbook root by root-relative name, relative-to-including-file, local vault over global home, and global home when the vault has none — each asserting a marker line unique to the partial that won.
- [ ] The core-tier case includes a partial shipped under `playbooks/_partials/` and asserts a line of its real text; the case comments why no fixture can supply that tier.
- [ ] A later-wave step fetched with `--step` resolves a playbook-directory include, proving the chain is identical on the step surface.
- [ ] A missing include renders `**STOP — tell the user:** Jinja rendering of step '{step}' failed:` with `TemplateNotFound` in the message, no `Traceback`, at exit 0.

### Task 5.2

- [ ] A case declaring a macro in `fixtures/xdg/booping/config.yaml` and passing `--stub-macro core.macros.{name}={literal}` shows the literal in the rendered body without the command running.
- [ ] A Jinja preamble calling `macro()` renders the stubbed stamp in the composed output.
- [ ] An unstubbed macro whose argv is a real command (`echo`-shaped, as in the `frontmatter-update` corpus) renders its captured stdout, proving the subprocess boundary is crossed.
- [ ] A `--step` render carries the stubbed value as well.

## Verify

```
cd booping-python && uv run pytest e2e -k render-playbook
```

Every case passes without `--txtar-update`, and a follow-up `--txtar-update` run leaves the working tree clean.
