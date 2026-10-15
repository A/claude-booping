from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel

_NAME = r"[A-Za-z0-9][A-Za-z0-9._-]*"
_PLAYBOOK_RE = re.compile(rf"^{_NAME}$")
_STEP_RE = re.compile(rf"^({_NAME})/({_NAME})$")
_AGENT_RE = re.compile(r"^agent:([A-Za-z0-9][A-Za-z0-9._:-]*)$")
_SKILL_RE = re.compile(r"^skill:([A-Za-z0-9][A-Za-z0-9._:-]*)$")


class Target(BaseModel):
    kind: Literal["playbook", "step", "agent", "skill"]
    playbook: str | None = None
    step: str | None = None
    agent: str | None = None
    skill: str | None = None


class TargetRejection(BaseModel):
    entry: str
    reason: str


def parse_target(entry: object) -> Target | TargetRejection:
    """Classify one `targets:` entry: `{playbook}`, `{playbook}/{step}`, `agent:{id}` or
    `skill:{name}`. Exact names only — anything else is rejected."""
    if not isinstance(entry, str):
        return TargetRejection(entry=str(entry), reason="not a string")
    value = entry.strip()
    if value != entry or not value:
        return TargetRejection(entry=entry, reason="not a target expression")
    agent = _AGENT_RE.match(value)
    if agent:
        return Target(kind="agent", agent=agent.group(1))
    skill = _SKILL_RE.match(value)
    if skill:
        return Target(kind="skill", skill=skill.group(1))
    step = _STEP_RE.match(value)
    if step:
        return Target(kind="step", playbook=step.group(1), step=step.group(2))
    if _PLAYBOOK_RE.match(value):
        return Target(kind="playbook", playbook=value)
    return TargetRejection(entry=entry, reason="not a target expression")
