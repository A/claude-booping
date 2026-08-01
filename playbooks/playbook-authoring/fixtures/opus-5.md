# Materialize one step's fixtures

The input names the target step and carries its confirmed contract and example, its confirmed
test plan, and answers to any questions you returned earlier. Produce the **fixture files** —
the ground every check stands on: real files materializing exactly what the test plan
describes. Its `## Fixtures` table says what each contains; its test rows say what each is
for. A wrong corpus makes every check either vacuous or flaky.

## The files to write

`<name>/<step>/_fixtures/*` — one file per fixture the rows name, nothing more:

- a fixture mirrors the input the step would actually receive from its upstream steps — a
  realistic input state, compact
- no fixture a test doesn't use; no test naming a fixture that doesn't exist
- a trap fixture carries exactly the flaw its row provokes, nothing else — a happy-path
  fixture carries no flaw beyond what its rows name

## Return format

```
## Changed:
- [CREATED] <name>/<step>/_fixtures/<fixture>.md

## Questions:
```

`## Questions:` only when a row's fixture is ambiguous to materialize — which flaw, how
realistic, what scale; empty otherwise.
