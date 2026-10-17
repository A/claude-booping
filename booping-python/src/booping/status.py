"""The computed project status — one ordered table of sections, each a summary line
and a detail body over one `StatusContext`. Nothing here prints or writes;
`booping.commands.status` is the argparse shell over it."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from functools import cached_property
from typing import Any

from booping import runs
from booping.context import Context
from booping.query import QueryError, as_dict, build_spec, resolve_spec, run
from booping.specs import open_items
from booping.specs.open_items import Mark
from booping.specs.records import Record, load_tier, unreviewed
from booping.specs.tiers import Tier, status_enum

PLAN_PLAYBOOKS = ("groom", "develop")
PLAN_STATE = "run"
ACTIVE_PLANS = "core.status.queries.active_plans"
UNREVIEWED_PLANS = "core.status.queries.unreviewed_plans"
RETRO_PLANS = "core.retro_playbook.queries.candidates"
TIER = "project"
IDEA_TYPE = "idea"
MARK_KINDS = ("clarify", "unknown")
CLARIFY = "clarify"
RUN_COLUMNS = [
    "id",
    "playbook",
    "mode",
    "items",
    "status",
    "started_at",
    "ended_at",
    "exit_code",
    "log",
]


class StatusError(Exception):
    pass


Table = tuple[list[dict[str, Any]], list[str]]


@dataclass
class StatusContext:
    """The booping `Context` plus the vault reads the sections share, each made once
    per call."""

    ctx: Context

    @cached_property
    def item_statuses(self) -> list[str]:
        return open_items.open_statuses(open_items.machine(self.ctx))

    @cached_property
    def items(self) -> Table:
        return open_items.index_rows(self.ctx, {"status:in": self.item_statuses})

    @cached_property
    def waiting(self) -> list[dict[str, Any]]:
        """Items in `clarify` — asked the user a question — by id."""
        rows = [row for row in self.items[0] if row.get("status") == CLARIFY]
        return sorted(rows, key=lambda r: str(r.get("id")))

    @cached_property
    def plan_statuses(self) -> list[str]:
        """Non-terminal statuses of groom's then develop's `run` machine, first
        occurrence wins."""
        statuses: list[str] = []
        for name in PLAN_PLAYBOOKS:
            pb = next((p for p in self.ctx.playbooks if p.name == name), None)
            if pb is None or PLAN_STATE not in pb.states:
                raise StatusError(f"playbook `{name}` declares no `{PLAN_STATE}` machine")
            statuses += [
                s for s in open_items.open_statuses(pb.states[PLAN_STATE]) if s not in statuses
            ]
        return statuses

    def _plans(self, path: str, overrides: dict[str, Any] | None = None) -> Table:
        try:
            spec = build_spec(self.ctx.config, resolve_spec(self.ctx.config, path), overrides)
            rows = [as_dict(row) for row in run(spec, self.ctx.vault)]
        except QueryError as exc:
            raise StatusError(str(exc)) from exc
        return rows, [*(spec.columns or []), "path"]

    @cached_property
    def active_plans(self) -> Table:
        return self._plans(ACTIVE_PLANS, {"where": {"status:in": self.plan_statuses}})

    @cached_property
    def unreviewed_plans(self) -> Table:
        return self._plans(UNREVIEWED_PLANS)

    @cached_property
    def retro_plans(self) -> Table:
        return self._plans(RETRO_PLANS)

    @cached_property
    def runs(self) -> list[dict[str, Any]]:
        """Run records nobody acked, by id, each with its effective status."""
        return [
            record | {"status": runs.effective_status(record)}
            for record in runs.records(self.ctx)
            if record.get("acked_at") is None
        ]

    @cached_property
    def record_types(self) -> list[str]:
        return self.tier.types if self.tier is not None else []

    @cached_property
    def idea_open(self) -> str | None:
        """The idea schema's first status — the one a new idea is written with, open
        until checked; the tier's `_schemas/` overlay may rename it."""
        schema = self.tier.schemas.get(IDEA_TYPE) if self.tier is not None else None
        enum = status_enum(schema) if schema is not None else []
        return enum[0] if enum else None

    @cached_property
    def tier(self) -> Tier | None:
        return next((t for t in self.ctx.specs_tiers if t.name == TIER), None)

    @cached_property
    def records(self) -> list[Record]:
        """The project tier's records of a known type, in type then file order."""
        if self.tier is None:
            return []
        known = self.record_types
        return [r for r in load_tier(self.tier, known) if r.type in known]

    def ref(self, record: Record) -> str:
        root = self.tier.root if self.tier is not None else record.path.parent.parent
        return open_items.record_ref(root, record.path)

    @cached_property
    def marks(self) -> list[Mark]:
        return open_items.marks(self.records, self.tier.root) if self.tier is not None else []


@dataclass(frozen=True)
class Section:
    name: str
    summary: Callable[[StatusContext], str]
    detail: Callable[[StatusContext], str]


def _counts(labels: list[str], values: list[str]) -> str:
    counted = Counter(values)
    return ", ".join(f"{counted[label]} {label}" for label in labels if counted[label])


def _items_summary(sc: StatusContext) -> str:
    rows, _ = sc.items
    if not rows:
        return "items: none"
    statuses = _counts(sc.item_statuses, [str(row.get("status")) for row in rows])
    sources = Counter(
        str(row.get("source")) if row.get("source") in open_items.REQUEST_SOURCES else None
        for row in rows
    )
    split = [f"{source} {sources[source]}" for source in open_items.REQUEST_SOURCES]
    split.append(f"spec gap {sources[None]}")
    line = f"items: {statuses} — {', '.join(split)}"
    if sc.waiting:
        line += f" — {len(sc.waiting)} waiting on you"
    return line


def _items_detail(sc: StatusContext) -> str:
    detail = _table(sc.items)
    if sc.waiting:
        waiting = _table((sc.waiting, ["id", "title"]))
        detail += f"\n\nWaiting on you:\n\n{waiting}"
    return detail


def _table(table: Table) -> str:
    rows, columns = table
    return open_items.index_table(rows, columns) if rows else "none"


def _open_ideas(sc: StatusContext) -> list[dict[str, Any]]:
    taken = {str(row.get("record")).split("#")[0] for row in sc.items[0] if row.get("record")}
    ideas = [
        {
            "ref": sc.ref(r),
            "title": r.frontmatter.get("title"),
            "created_at": r.frontmatter.get("created_at"),
        }
        for r in sc.records
        if r.type == IDEA_TYPE and sc.idea_open and r.frontmatter.get("status") == sc.idea_open
    ]
    return [idea for idea in ideas if idea["ref"] not in taken]


def _ideas_summary(sc: StatusContext) -> str:
    ideas = _open_ideas(sc)
    return f"ideas: {len(ideas)} open, not taken" if ideas else "ideas: none"


def _ideas_detail(sc: StatusContext) -> str:
    return _table((_open_ideas(sc), ["ref", "title", "created_at"]))


def _plans_summary(sc: StatusContext) -> str:
    rows, _ = sc.active_plans
    active = _counts(sc.plan_statuses, [str(row.get("status")) for row in rows])
    line = f"plans: {active}" if active else "plans: none active"
    unreviewed, no_retro = len(sc.unreviewed_plans[0]), len(sc.retro_plans[0])
    if unreviewed or no_retro:
        line += f" — done: {unreviewed} without code review, {no_retro} without retro"
    return line


def _plans_detail(sc: StatusContext) -> str:
    return "\n\n".join(
        f"### {heading}\n\n{_table(table)}"
        for heading, table in (
            ("active", sc.active_plans),
            ("without code review", sc.unreviewed_plans),
            ("without retro", sc.retro_plans),
        )
    )


def _runs_summary(sc: StatusContext) -> str:
    counts = _counts(list(runs.STATUSES), [str(r.get("status")) for r in sc.runs])
    return f"runs: {counts}" if counts else "runs: none"


def _runs_detail(sc: StatusContext) -> str:
    return _table((sc.runs, RUN_COLUMNS))


def _unreviewed(sc: StatusContext) -> list[Record]:
    return [r for r in sc.records if unreviewed(r)]


def _records_summary(sc: StatusContext) -> str:
    records = _unreviewed(sc)
    if not records:
        return "records: none unreviewed"
    counted = Counter(r.type for r in records)
    by_type = ", ".join(f"{t} {counted[t]}" for t in sc.record_types if counted[t])
    return f"records: {len(records)} unreviewed — {by_type}"


def _records_detail(sc: StatusContext) -> str:
    rows = [
        {
            "ref": sc.ref(r),
            "status": r.frontmatter.get("status"),
            "title": r.frontmatter.get("title"),
        }
        for r in _unreviewed(sc)
    ]
    return _table((rows, ["ref", "status", "title"]))


def _marks_summary(sc: StatusContext) -> str:
    if not sc.marks:
        return "marks: none"
    counted = Counter(m.kind for m in sc.marks)
    kinds = ", ".join(f"{kind} {counted[kind]}" for kind in MARK_KINDS)
    return f"marks: {len(sc.marks)} — {kinds}"


def _marks_detail(sc: StatusContext) -> str:
    rows = [{"kind": m.kind, "record": m.record, "text": m.text} for m in sc.marks]
    return _table((rows, ["kind", "record", "text"]))


SECTIONS: tuple[Section, ...] = (
    Section("items", _items_summary, _items_detail),
    Section("ideas", _ideas_summary, _ideas_detail),
    Section("plans", _plans_summary, _plans_detail),
    Section("runs", _runs_summary, _runs_detail),
    Section("records", _records_summary, _records_detail),
    Section("marks", _marks_summary, _marks_detail),
)
