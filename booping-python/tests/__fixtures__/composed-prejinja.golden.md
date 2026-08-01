# Composed Procedure

Plain prose preamble that must pass through verbatim, including this literal
token: {{ leftover }} — no Jinja evaluation happens here.

## Execution graph

```mermaid
flowchart TD
  gather --> draft
  gather --> named-step
  draft --> plain
  named-step --> plain
```

Steps on one line run in parallel — spawn all their sub-agents in one message,
wait for all to finish, then start the next wave.

1. `gather`
2. `draft` ∥ `named-step`
3. `plain`

## Gather

Instructions:
- Summary: Gather inputs.
- Run in a sub-agent — model sonnet, effort medium.

Run `booping render-playbook composed --step gather` for content.

## Draft

Instructions:
- Summary: Draft the artifact.
- After: gather
- Parallel with: named-step
- Run in a sub-agent — model opus, effort high.
- Review gate: stop after this step — "confirm the draft before continuing"; continue only on explicit user confirmation.

Run `booping render-playbook composed --step draft` for content.

## Named Step

Instructions:
- Summary: A step delegated to a named agent.
- After: gather
- Parallel with: draft
- Run in sub-agent: booping-researcher.
- Review gate: stop after this step — "sign off the research"; continue only on explicit user confirmation.

Run `booping render-playbook composed --step named-step` for content.

## Plain

Instructions:
- Summary: A plain step with no delegation and no gate.
- After: draft, named-step

Run `booping render-playbook composed --step plain` for content.
