# Composed Procedure

Plain prose preamble that must pass through verbatim, including this literal
token: {{ leftover }} — no Jinja evaluation happens here.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `gather` | — | Gather inputs. | — |
| `draft` | `gather` | Draft the artifact. | confirm the draft before continuing |
| `named-step` | `gather` | A step delegated to a named agent. | sign off the research |
| `plain` | `draft`, `named-step` | A plain step with no delegation and no gate. | — |

## Step: Gather

Gather inputs.

Tell a sub-agent — model sonnet, effort medium — to get its instructions by calling this command: `booping render-playbook composed --step gather`.

## Step: Draft

Draft the artifact.

Review gate: stop after this step — "confirm the draft before continuing"; continue only on explicit user confirmation.

Tell a sub-agent — model opus, effort high — to get its instructions by calling this command: `booping render-playbook composed --step draft`.

## Step: Named Step

A step delegated to a named agent.

Review gate: stop after this step — "sign off the research"; continue only on explicit user confirmation.

Tell the `booping-researcher` agent to get its instructions by calling this command: `booping render-playbook composed --step named-step`.

## Step: Plain
Instructions:
- Summary: A plain step with no delegation and no gate.
- After: draft, named-step

Run `booping render-playbook composed --step plain` for content.
