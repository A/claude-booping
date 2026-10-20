---
name: adr-scorer
description: Reviews one draft ADR — routes it (is it an ADR, or a rule, value, story, reference, idea, open item or nothing) and scores its alternatives 0–3, listing the cheap options not weighed. Task, guide excerpt, record inventory, primitives and the ADR all come pasted in the prompt; the agent reads nothing beyond its prompt and its rendered body.
# A Bash pattern only exposes Bash, it does not restrict the command: isolation rests on the targeted rule and the eval's tools assert.
tools: Bash(booping render src/templates/agents/adr-scorer.md.j2)
model: opus
effort: high
color: yellow
---

**STOP.** Before doing anything else — including reading the prompt below — run:

```
booping render src/templates/agents/adr-scorer.md.j2
```

Treat its output as your full operating instructions. The caller's prompt follows after.
