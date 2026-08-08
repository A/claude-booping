---
status: awaiting-prompt-confirm
reviewed_at: 20260804 17:46
fixtures_reviewed_at: 20260804 17:46
---

[← index](../../index.md)

# review

## Contract

- **Needs** —
  - the confirmed review scope — a diff range or a file list, with the plan behind it when there
    is one
  - that plan's DoD, mandated approach and architectural decisions, when a plan is in scope
  - the project's accumulated lessons
  - the available review checklists with their names, layers and descriptions
  - the repo's stack signals — manifests, framework, linter, formatter, type-checker, test runner
  - the changed code itself
- **Value** — the run's whole review value, produced in one detached pass so the diff, the
  checklists and the lessons never enter the runner's context. The pass walks the craft in order:
  discover the stack from the manifests and the tooling actually configured, pick the checklists
  that match it (every generic one; a language or framework one only on a real signal in the
  repo), map blast radius for a wide diff, walk every item of every loaded checklist against the
  changed code, then the three dynamic checks a static checklist cannot carry — lesson
  compliance, plan-DoD alignment, plan-intent match. Style the project's linter or formatter
  already enforces is filtered out as noise. A lesson violation is a `BLOCKER`, never softened.
  Ambiguity — a mixed-language repo, two type-checkers configured, an unclear checklist fit, a
  plan with no commit baseline — is judged here and stated in the return, never bounced back as a
  question: the step runs unattended and has no gate to hold it.
- **Output files** —
  - none — nothing is written to the vault, to the repo or to a temp file; the findings are the
    return block itself
- **Harness return** — richer than the harness default: a `## Findings:` section ahead of the
  three standard ones, carrying one entry per finding — severity · file and line anchor ·
  offending snippet · proposed fix as an exact replacement snippet · one-line rationale citing the
  checklist item or lesson id — grouped `BLOCKER` → `SUGGESTION` → `NIT`. `## Changed:` is always
  empty. `## Notes:` carries the stack read, the checklists loaded with a one-line reason each,
  and every ambiguity judged. `## Questions:` is always empty.
- **Review gate** —
  - none — the findings are what the human reviews next, in `present`
- **Delegation** — detached; generic sub-agent at `opus-5:high`

## Example artifact

````markdown
## Findings:

- **BLOCKER** · `src/api/routes.py:88` · lesson `0007_validate-at-the-boundary`
  ```python
  payload = request.json()
  user = User.objects.get(id=payload["id"])
  ```
  fix:
  ```python
  payload = CreateUserRequest.model_validate(request.json())
  user = User.objects.get(id=payload.id)
  ```
  rationale: unvalidated boundary input reaches the ORM — lesson `0007` requires an explicit
  schema at every external edge.

- **BLOCKER** · `src/api/routes.py:120` · plan DoD "rate limit on the create endpoint"
  ```python
  @router.post("/users")
  async def create_user(request: Request) -> Response:
  ```
  fix: apply the project's existing `@rate_limit(...)` decorator, as the two sibling write
  endpoints do.
  rationale: the DoD item is checked `[x]` in the plan but the diff ships no limiter — DoD
  alignment.

- **SUGGESTION** · `src/services/user.py:41` · `coding-architecture` — Dependency Inversion / DI
  seams
  ```python
  self.mailer = SmtpMailer(settings.SMTP_URL)
  ```
  fix:
  ```python
  def __init__(self, mailer: Mailer) -> None:
      self.mailer = mailer
  ```
  rationale: the collaborator is constructed inline, so the new test has to monkey-patch it.

- **NIT** · `src/services/user.py:57` · `python` — specific exception types
  ```python
  raise Exception("user exists")
  ```
  fix:
  ```python
  raise UserAlreadyExists(email)
  ```
  rationale: the module already defines the typed error one level up.

## Changed:

## Notes:

- stack: Python 3.12 · FastAPI · uv · ruff (formatter + linter) · basedpyright · pytest
- checklists loaded: `coding-architecture` and `security` (generic, always), `python` (language —
  `pyproject.toml` + the whole diff is Python); no framework checklist matched FastAPI
- 14 changed files, so blast radius was mapped first: the diff touches the user-creation path and
  the public `/users` API only
- ruff-owned formatting and import-order findings were dropped, not reported
- ambiguity judged: the repo configures both mypy and basedpyright; basedpyright is the one wired
  into `just typecheck`, so type findings were written against it

## Questions:
````

## Return Format

````markdown
## Findings:

- **{BLOCKER|SUGGESTION|NIT}** · `{file}:{line}` · {checklist item, lesson id, or dynamic check}
  ```{lang}
  {offending snippet}
  ```
  fix:
  ```{lang}
  {exact replacement snippet}
  ```
  rationale: {one line}

## Changed:

## Notes:

- {stack read; checklists loaded with a one-line reason each; ambiguity judged}

## Questions:
````
