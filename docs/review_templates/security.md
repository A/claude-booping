---
name: security
description: Generic security checklist — input validation, secrets, auth, dependencies, injection, output handling.
layer: generic
---

# Quality Checklist

- [ ] Boundary input validation — every external input (HTTP, CLI, queue, file) is validated at the boundary against an explicit schema; trust does not propagate inward unchecked.
- [ ] Secrets via environment — credentials, tokens, and keys are read from environment / the project's configured secret store; no secrets committed to source, no fallback defaults.
- [ ] Auth before resource access — authentication and authorisation checks run before any side-effectful or data-returning operation; no code paths bypass the check.
- [ ] Dependency hygiene & lockfile — new dependencies are pinned; the project's lockfile is updated and committed; no unmaintained or known-vulnerable packages introduced.
- [ ] Injection prevention — queries, shell calls, and templated strings use parameterisation / escaping appropriate to the sink; no string concatenation of untrusted input into a privileged context.
- [ ] Output sanitisation — data crossing back to a caller is encoded for its destination (HTML, log, JSON); error messages don't leak internals (stack traces, query fragments, secret material).
