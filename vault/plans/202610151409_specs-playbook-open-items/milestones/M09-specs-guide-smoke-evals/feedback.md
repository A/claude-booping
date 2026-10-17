# Feedback — M09

**Blocked (1/2)**: `playbooks/specs/guide/tests.yaml` carries a verbatim copy of `src/specs/schemas/adr.yaml` as the mdcheck `rules:` block — a second source of the ADR shape that drifts when the schema changes ([value/0003](../../../../specs/value/0003-single-source.md)). The learn/write precedent writes case-specific rules, never a schema copy.

Checked: the worker's report, `playbooks/_lib/asserts/mdcheck.js` (inline `rules` only), `playbooks/learn/write/tests.yaml`.

Next attempt: give the shared `playbooks/_lib/asserts/mdcheck.js` a `rulesFile` param — a path resolved against the plugin root (the repo root, found from the module's own location), read verbatim and handled exactly like `rules` (bare list wrapped, full rule file passed through); `rules` and `rulesFile` together is a loud error. Document it in the module's Params header. Point the specs/guide ADR assert at `rulesFile: src/specs/schemas/adr.yaml` and delete the copy. The `context:` entry naming the schema stays. Rerun `EVAL_PR=0 just smoke specs/guide` once and also `just smoke learn/write` to show the existing `rules` path still works. Everything else in M09 stands.
