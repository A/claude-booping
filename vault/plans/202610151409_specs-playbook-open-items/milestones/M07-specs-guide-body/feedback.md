# Feedback — M07

**Blocked (1/2)**: tier roots are resolved in Jinja inside `playbooks/specs/playbook.md` — an `under()` macro plus a copy of `tiers.project_root`'s null-path fallback (`{vault}/specs` vs `{repo}/specs`).

Checked: the worker's report and the rendered preamble. The DoD line "tier paths render from config" passes, but the template re-implements path resolution the code already owns: [value/0003](../../../../specs/value/0003-single-source.md) (single source — the fallback now lives twice and can drift) and [rule/0025](../../../../specs/rule/0025-mechanics-run-as-code.md) (computable mechanics run as code). A choice that contradicts a value or rule is wrong.

Next attempt: expose the resolved tier roots from code — the same functions `booping specs` uses to resolve a tier (`tiers.project_root` and its siblings) — to the template context (e.g. a field on the `booping` template global, or a macro over a CLI verb, per M07 Scope's "from config or a macro"), and have the preamble only print them. No path logic in the template. Keep the render reproducible ([rule/0027](../../../../specs/rule/0027-renders-reproducible.md)): the hermetic fixture render must repeat byte for byte. Cover the new code with a unit test. Everything else in M07 stands.
