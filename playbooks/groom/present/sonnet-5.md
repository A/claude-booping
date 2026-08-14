Read the plan's milestone rows — never a hand-kept list — with `{plan-dir}` the preamble's `Plan dir:` line:

```
booping query --glob {plan-dir}/{{ config.core.plans.milestones.glob }} --columns {{ config.core.plans.milestones.table_columns | join(',') }}
```

Present user the resulting plan as:

```
Request: {path}
Plan: {path}
Status: {status}
SPs: {sum of the rows' sp}

{the table the query printed}

## Next Steps

Approve plan or jump into develop via:

/playbook develop {plan path}
```

{% if config.core.tracker.driver == 'linear' -%}
## Publish the plan to the tracker

Four calls, in this order. `{plan-issue-ref}` is the identifier the first receipt printed; `{request}` is `index.md`'s `tracker_request`.

1. The plan issue:

   ```
   booping-tracker issue-create --team {{ config.core.tracker.linear.team }} --title "{plan title}" --body-file {plan-dir}/index.md --label {{ config.core.tracker.linear.playbooks.groom.labels.plan }}
   ```

2. One sub-issue per milestone file the table above listed — in milestone order, `{id}` and `{title}` read from that file's own frontmatter, `{milestone-file}` its path:

   ```
   booping-tracker issue-create --team {{ config.core.tracker.linear.team }} --title "M{id} — {title}" --body-file {milestone-file} --parent {plan-issue-ref}
   ```

3. The cross-link back to the request issue:

   ```
   booping-tracker relate --issue {plan-issue-ref} --to {request} --type related
   ```

4. The recorded ref — never by hand-editing frontmatter:

   ```
   booping frontmatter-update {plan-dir}/index.md tracker_issue={plan-issue-ref}
   ```

Then `booping playbook-transition groom awaiting-approval --workdir {plan-dir}` and **end the run**. Approval is not asked for here and this step's `Review gate:` line does not apply — it arrives as a status move on the plan issue, which starts the next invocation.
{% else -%}
Ask for approval in **prose**, in the message itself — never through `AskUserQuestion`, and
never as a `## Questions:` entry. One plain sentence after the screen: the plan is ready for
development, or say what to change. Read the reply as chat text; "looks good" approves,
silence does not.

Open questions that are not the approval ask still go in a `## Questions:` block below the
table.
{%- endif %}
