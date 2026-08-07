# code-review playbook

Code review is a **playbook**, not a skill. Run it with:

```text
/playbook code-review
```

A run reviews one confirmed scope end to end — `scope` settles what to look at (a plan from the review queue, the latest commits, or a named target), `review` returns severity-classified findings from a detached pass, `present` collects your verdict, and `resolve` acts on it. The run is ephemeral: no workdir, no persisted state, no review artefact, so a second look after fixes is a new run.

See [Playbooks → Shipped playbooks](playbook.md#shipped-playbooks) for how playbooks are driven, and [Vault → `review_templates/`](vault.md#review_templates) for project-local review checklists.
