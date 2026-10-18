# ADR alternatives rubric

Score the ADR 0–3:

- 3: the alternatives include the cheapest credible option(s) (prose/prompt, an existing primitive extended or generalised, or doing nothing — whichever apply) and each gets honest pros; the decision would survive a skeptic.
- 2: real alternatives, but one obvious cheap option is missing.
- 1: the alternatives are a straw man / a restatement ("one fixed mode", "what we do today") — the table exists to satisfy the schema.
- 0: no real choice was weighed (the record is really a rule, or the alternative is absurd).

## Cheap options

Check each against the alternatives; one that applies and is missing or dismissed without honest pros is a finding:

- **prose** — a line in a prompt, a guide or a rule record instead of a mechanism;
- **extending an existing primitive** — an existing command, key, hook or record type generalised to cover the case;
- **building nothing** — the cost of leaving things as they are.

## Output

First line `score: {0-3}`, then one line per finding — a missing or straw-man alternative, named in a few words. A score of 3 has no finding lines. Nothing else.
