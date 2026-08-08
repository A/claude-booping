# Interview the playbook request

The input is a user's description of a playbook they want, plus — on a later iteration — their
answers to questions you returned earlier, and the brief you already wrote if one exists. You
run fresh each time; the brief and the answers are your only memory. Produce the **brief**: the
few answers every later step of playbook authoring builds on, inferred from what the user
already said. The user is asked ONLY about real gaps — a question whose answer is already in
the input, or in the existing brief, wastes their gate.

## What to settle

- **Slug** — kebab-case, the new playbook's directory name. If the description names it, take
  it; otherwise ask, offering two or three candidates plus a free-input option.
- **Goal** — what the playbook does, one clear paragraph reflecting the user's own words.
- **Success result** — what done looks like for a run, one paragraph.
- **Artifact home** — where the playbook keeps the process files the user reviews. A single
  path, nothing else.
- **Wishes** — desires the description states that the playbook must address: review points,
  decomposition suggestions, style constraints. Only what the user actually said.

## The file to write

`<slug>/_specs/brief.md`, created or updated — only once the slug is settled; before that,
write nothing and ask. The file is a clean artifact: questions never live in it.

```markdown
# <slug> — Brief

## Goal

<one paragraph>

## Success result

<one paragraph>

## Artifact home

`<path>`

## Wishes

- <bullet list; omit the section when the user stated no wishes>
```

On update preserve any existing frontmatter — `reviewed_at` and other stamps are
harness-owned; never write one yourself.

## Questions

An answered question is never asked again — fold the answer in and move on. No questions
left means the interview is complete.

## Return format

```
## Changed:

- [CREATED] <slug>/_specs/brief.md

## Questions:

1. <question>
```

`## Questions:` is empty when the interview is complete; then add:

```
## Answers:

- slug: <slug>
- goal: <one line>
- success: <one line>
- artifact home: <path>
```

Paths are relative to the destination root.
