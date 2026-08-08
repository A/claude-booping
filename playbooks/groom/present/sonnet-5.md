Present user the resulting plan as:

```
Request: {path}
Plan: {path}
Status: {status}
SPs: {SP total}

| # | Summary | SP |
| - | ------- | -- |
{one row per milestone — its id, what it delivers, its SP}

## Next Steps

Approve plan or jump into develop via:

/playbook develop {plan path}
```

Ask for approval in **prose**, in the message itself — never through `AskUserQuestion`, and
never as a `## Questions:` entry. One plain sentence after the screen: the plan is ready for
development, or say what to change. Read the reply as chat text; "looks good" approves,
silence does not.

Open questions that are not the approval ask still go in a `## Questions:` block below the
table.
