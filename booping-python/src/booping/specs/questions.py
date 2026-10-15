"""Questions on an open item — the `docs/clarifications.md` format, one sidecar per
item under `{vault}/{core.specs.open_items.dir}/questions/{id}.md`.

Every read and write of a sidecar lives here; nothing is printed.
`booping.commands.items` is the argparse shell over `ask` and `answer`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from booping.commands.playbook_transition import read_status
from booping.context import Context
from booping.specs import open_items
from booping.specs.open_items import OpenItemError

SUBDIR = "questions"
OPEN = "open"
ANSWERED = "answered"
ANSWER_LABEL = "**Answer:**"

_HEADING = re.compile(r"^## (C(\d+)) — (.*) — (\S+)\s*$")
_NUMBER = re.compile(r"^## C(\d+) ", re.MULTILINE)
_FENCE = re.compile(r"^\s{0,3}(```|~~~)")


@dataclass(frozen=True)
class Question:
    id: str
    topic: str
    state: str
    answer: str
    heading: int
    label: int | None
    end: int


def sidecar_path(ctx: Context, item_id: str) -> Path:
    return open_items.items_dir(ctx) / SUBDIR / f"{item_id}.md"


def _blocks(lines: list[str]) -> list[tuple[int, int]]:
    """`(start, end)` line spans of each H2; an H2-looking line inside a fence is body."""
    starts: list[int] = []
    fence: str | None = None
    for index, line in enumerate(lines):
        match = _FENCE.match(line)
        if match is not None:
            fence = None if fence == match.group(1) else (fence or match.group(1))
        elif fence is None and line.startswith("## "):
            starts.append(index)
    return list(zip(starts, [*starts[1:], len(lines)], strict=True))


def parse(text: str) -> list[Question]:
    lines = text.splitlines()
    questions: list[Question] = []
    for start, end in _blocks(lines):
        heading = _HEADING.match(lines[start])
        if heading is None:
            continue
        label = next((i for i in range(start + 1, end) if lines[i].startswith(ANSWER_LABEL)), None)
        answer = (
            "\n".join([lines[label][len(ANSWER_LABEL) :], *lines[label + 1 : end]])
            if label is not None
            else ""
        )
        questions.append(
            Question(
                id=heading.group(1),
                topic=heading.group(3),
                state=heading.group(4),
                answer=answer,
                heading=start,
                label=label,
                end=end,
            )
        )
    return questions


def is_answered(question: Question) -> bool:
    return question.state == ANSWERED and any(line.strip() for line in question.answer.splitlines())


def read(ctx: Context, item_id: str) -> list[Question]:
    path = sidecar_path(ctx, item_id)
    return parse(path.read_text(encoding="utf-8")) if path.is_file() else []


def open_count(ctx: Context, item_id: str) -> int:
    return sum(1 for q in read(ctx, item_id) if not is_answered(q))


def _require_item(ctx: Context, item_id: str) -> Path:
    path = open_items.item_path(ctx, item_id)
    if not path.is_file():
        raise OpenItemError(f"unknown item {item_id}")
    return path


def ask(
    ctx: Context,
    item_id: str,
    *,
    topic: str,
    question: str,
    options: list[str],
    step: str,
) -> str:
    """Append the next `C{n}` to the item's sidecar; returns `{sidecar}#C{n}`."""
    status = read_status(_require_item(ctx, item_id))
    if status not in open_items.open_statuses(open_items.machine(ctx)):
        raise OpenItemError(f"item {item_id} is {status}")
    path = sidecar_path(ctx, item_id)
    existing = path.read_text(encoding="utf-8") if path.is_file() else f"# Questions — {item_id}\n"
    number = max((int(n) for n in _NUMBER.findall(existing)), default=0) + 1
    entry = [
        f"## C{number} — {topic} — {OPEN}",
        "",
        f"**Asked:** {open_items.today(ctx)} — {step}",
        "",
        f"**Question:** {question}",
        "",
    ]
    if options:
        entry += ["**Options:**", "", *(f"- {option}" for option in options), ""]
    entry.append(ANSWER_LABEL)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(existing.rstrip("\n") + "\n\n" + "\n".join(entry) + "\n", encoding="utf-8")
    return f"{open_items.vault_relative(ctx, path)}#C{number}"


def answer(ctx: Context, item_id: str, question_id: str, text: str) -> str:
    """Write *text* verbatim under the question's `**Answer:**` and mark it answered;
    returns `{sidecar}#C{n}`."""
    _require_item(ctx, item_id)
    path = sidecar_path(ctx, item_id)
    content = path.read_text(encoding="utf-8") if path.is_file() else ""
    target = next((q for q in parse(content) if q.id == question_id), None)
    if target is None:
        raise OpenItemError(f"unknown question {item_id} {question_id}")
    if is_answered(target):
        raise OpenItemError(f"question {item_id} {question_id} is already answered")
    if not text.strip():
        raise OpenItemError("--text is blank")
    lines = content.splitlines()
    lines[target.heading] = f"## {target.id} — {target.topic} — {ANSWERED}"
    head = lines[: target.label if target.label is not None else target.end]
    while head and not head[-1].strip():
        head.pop()
    rebuilt = "\n".join([*head, "", ANSWER_LABEL, "", text])
    if not text.endswith("\n"):
        rebuilt += "\n"
    tail = lines[target.end :]
    if tail:
        rebuilt += "\n" + "\n".join(tail) + "\n"
    path.write_text(rebuilt, encoding="utf-8")
    return f"{open_items.vault_relative(ctx, path)}#{question_id}"
