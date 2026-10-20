# Specs alignment guide

An interview that settles what the project values, then the boundaries of how the model works that follow from those values. Record types, files and frontmatter are in [the specs format guide](../src/specs/README.md); this guide covers only the order and the questions.

The user can leave at any point. Whatever is settled by then stays recorded; the rest is picked up the next time the user asks.

## Order

Each stage builds on the ones before it, so keep the order and finish a stage before starting the next:

1. **Values and non-values** — what the project protects, and what it explicitly does not care about.
2. **Conflicts** — where two values pull apart, and which one wins when.
3. **Rules** — the constraints that follow from each value.
4. **ADRs** — only for choices the project has already made. Never draft a decision here.

Read the tier's existing records first (`booping specs ls`), and ask only about what they do not already cover.

## Questions

One question pattern per stage. Ask one question at a time and build the next on the answer:

- **Values** — "When a change makes {X} worse to gain speed, do you accept it?" Ask about concrete trade-offs the project has faced, not abstract virtues. A "no, never" is a value; a shrug is a non-value worth recording too.
- **Conflicts** — "{Value A} and {value B} both apply to {situation}. Which wins, and does that change when {condition}?"
- **Rules** — "Given {value}, what must the model never do — or always do — when it {acts in this area}?"
- **ADRs** — "You chose {X} over {Y}. What made {Y} lose, and would that still hold today?"

## When to write a record

- A value or non-value the user stated → a `value` record.
- Two values with a stated resolution → a `conflict` record, linking both values.
- A constraint that follows from a value → a `rule` record, linking the value it follows from.
- A past choice with a real alternative and a reason → an `adr` record.

Write each record as soon as its stage settles it, following the preamble's record-writing steps.

A record states only what the user said. Do not fill gaps with a plausible guess: mark each one `[clarify]` at the start of its sentence, followed by the question the user still has to answer.
