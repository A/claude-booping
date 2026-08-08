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
- when the spec's Delegation is **assisted**: a line naming the heavy reads or research the
  runner hands to the configured researcher agent and the compressed summary it gets back —
  the runner still performs the step itself. Inline steps get no such line.
- no frontmatter, no Jinja or harness tokens — plain instructions only

`<name>/<step>/prompt.md` — the wrapper:

- frontmatter: `summary`, `review_gate` reproduced from the spec (or `null` when the spec
  gates nothing), and `detached:` only when the spec's Delegation is **detached**. Never
  `name:` — the dir name is the step name. Never `inputs:` or `outputs:` — the spec's Needs
  and Output files own the io and the runner resolves them. Never `agent:` — it is the
  legacy name of `detached:` and renders a blocking notice.
- `detached: <family>:<effort>` — family is the spec's model slug without its version
  (`opus-5:medium` → `opus:medium`), effort carried over unchanged; use a bare agent name
  instead only where the spec names a specific agent. Inline and assisted steps carry no
  delegation key at all.
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
