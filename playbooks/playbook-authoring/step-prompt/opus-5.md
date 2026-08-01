# Write one step's prompt

The input names the target step and carries its confirmed contract and example, the confirmed
manifest, and the target model. Produce the **step itself**: a minimal prompt body a fresh,
context-isolated consumer can execute, plus its wrapper. Seed quality on purpose — refinement
runs through the optimizer steps later; the body's document contract comes from the confirmed
spec: the contract bullets and the example artifact.

## The files to write

`<name>/<step>/<model>.md` — the body. `<model>` is the full model slug from the target
model: `opus-5:medium` names `opus-5.md`.

- what the step receives, in its own words
- the artifact: the file(s) to write, with the document contract matching the confirmed
  example — including any backlink obligation the spec's Output files state
- the harness return, verbatim
- no frontmatter, no Jinja or harness tokens — plain instructions only

`<name>/<step>/prompt.md` — the wrapper:

- frontmatter: `summary`, `agent: <family>:<effort>` — family is the model slug without its
  version (`opus-5:medium` → `opus:medium`) — `review_gate` reproduced from the spec (or
  `null` when the spec gates nothing), then `inputs:` and `outputs:`. Never `name:` — the
  dir name is the step name.
- `inputs:` — one entry per Needs bullet of the confirmed spec: `what:` carries the
  INFORMATION, artifact-blind, never a file path; add `from:` only when the source lies
  outside prior step returns (`user`, `runner`). The runner resolves each entry into the
  spawn prompt.
- `outputs:` — plain strings translating the spec's Output files and harness return; the
  runner turns them into the step's return contract.
- body: exactly one line — the Jinja include of the body file (percent-brace include syntax,
  the body filename in double quotes), nothing else

## Return format

```
## Changed:
- [CREATED] <name>/<step>/<model>.md
- [CREATED] <name>/<step>/prompt.md

## Notes:
- just verify-wrapper <name> <step> <model>.md
```
