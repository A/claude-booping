# What I want: a release-notes playbook

Call it `release-notes`. Every couple of weeks I cut a release and writing the notes by hand
is the part I keep putting off, so I want the procedure as a playbook.

What it should do: collect the merged PRs since the last tag, group them into features, fixes
and internal changes, and draft the notes in our house style — short lines, user-facing wording,
no ticket numbers in the text. I review the draft, fix the tone where it drifts, and only after
my sign-off does it get committed.

Done looks like this: a `NOTES-<version>.md` I have signed off, sitting in `releases/` at the
repo root next to the previous ones, plus the changelog line added to `CHANGELOG.md`. If the
draft needs my edits, that is normal — the point is I edit a draft instead of writing from
scratch.

Keep the working files — the raw PR list, the grouped draft, whatever the steps produce for me
to look at — in `releases/_work/<version>/`, so I can pick up a half-done release after a
weekend without re-running everything.
