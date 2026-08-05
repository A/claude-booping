{% set pending = 'migrations.pending' | query(where={'id:gt': booping.latest_migration}) -%}
# Open the migration run

## Ground

Confirm a project is attached, and name it and its vault path in the presentation.

The recorded migration id — the last migration this vault applied — is **{{ booping.latest_migration }}**,
read from the repo `.booping` marker's `latest_migration` key; `-1` means nothing has been applied yet.
If no project is attached, or that id came through as anything other than a number, say which and
end the run: nothing below resolves without it.

{% if pending %}
## Work in flight

Name what is uncommitted across the repo and the vault — counts plus the notable paths, not a full
listing — and ask the user to let you commit both before anything is transformed, so every
migration lands on a clean slate and stays independently revertable. Commit on confirmation. Skip
the ask when nothing is uncommitted.

Ask and resolve this here, inside the step: the commit has to land before the first migration runs,
which is why it cannot wait for the approval below. It is not the review gate and it never blocks —
a user who declines still proceeds. Detection and committing are yours at execution time; no git
mechanics belong in this instruction.

## The pending set

Every shipped migration with an id above the recorded one, resolved at render time:

{{ pending | as_table(columns=['id', 'title', 'summary']) }}

Present in chat, in this order: the project and its vault, the recorded id, the uncommitted-work
ask when there is one, then the table above verbatim under a
**{{ pending | length }} migrations pending:** heading, then what applying them entails —

- they apply in id order, one at a time
- each lands as its own commit and advances the recorded id, so an interrupted run resumes where it
  stopped and any single migration can be reverted on its own
- a migration that fails stops the run there: it gets named, with a proposed fix rather than a skip

Close on one question covering the whole set — `Apply all {{ pending | length }}?` —
asked in **prose**, in the message itself, never through `AskUserQuestion`. That approval authorises
every migration listed; nothing is asked per migration afterwards. Wait for the answer before the
run continues.

## Return

```markdown
## Changed:

## Notes:
- pending: {{ pending | length }} — {{ pending | map(attribute='id') | join(', ') }}
- committed repo and vault before proceeding (user confirmed)
- approved: apply the whole pending set
```

`## Changed:` stays empty — this step writes no file. Give each pending id its title in the
`pending:` line. Drop the commit line when nothing was uncommitted, and say so plainly instead of
claiming a commit that was declined.
{% else %}
## Already current

Nothing is pending: **{{ booping.latest_migration }}** is the latest migration the plugin ships.

Report it in one line — the project and its vault, the recorded id, that the vault is **already
current**, and that the run ends here. Ask nothing, commit nothing, and do not continue to the next
step.

## Return

```markdown
## Changed:

## Notes:
- pending: 0 — already current at recorded id {{ booping.latest_migration }}
- end the run: nothing to apply
```

`## Changed:` stays empty — this step writes no file.
{% endif %}
