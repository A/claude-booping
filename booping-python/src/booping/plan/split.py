"""Cut a one-file plan draft on its own headings into plan lines and milestones.

Pure: draft text in, a :class:`Cut` out. Every draft line lands in exactly one of
``plan_lines``, ``overview_lines``, ``marker_lines`` or one milestone section, verbatim
with its line ending. Markers are the old layout's scaffolding the milestone file
regenerates: milestone and section headings, separators at a block's edges, embedded
metadata.

Detection is tolerant on purpose (path headings, an embedded ``# M1 —``, metadata
tables): the draft prompt fixes one format, the parser forgives the rest.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

SECTION_KEYS: tuple[str, ...] = ("tasks", "dod", "references", "verify")

SECTION_NAMES: Mapping[str, str] = {
    "tasks": "tasks",
    "task list": "tasks",
    "work": "tasks",
    "definition of done": "dod",
    "dod": "dod",
    "acceptance": "dod",
    "acceptance criteria": "dod",
    "done when": "dod",
    "references": "references",
    "reference": "references",
    "refs": "references",
    "links": "references",
    "see also": "references",
    "verify": "verify",
    "verification": "verify",
    "how to verify": "verify",
}
# Headings inside the last milestone block that never end it.
BLOCK_HEADINGS = frozenset({"goal", "scope", "notes", "context", "files"})

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
MILESTONE_HEADING = re.compile(
    r"^#{1,4}\s+(?:.*?milestones/[Mm]0*(\d+)-|(?:Milestone\s+)?M0*(\d+)\b\s*(?:[—–:\-]|$))"
)
DEPENDS_TEXT = re.compile(
    r"(?:^|[·|`*\s-])depends(?:_on| on)?\**\s*[:|]\s*\**\s*((?:M\d|—|-|\[|none).*)", re.I
)
META_KEY = re.compile(
    r"^[`*]*(id|title|slug|sp|sp_estimated|depends_on|depends|depends on|status|plan|file|goal_sp)"
    r"[`*]*\s*:",
    re.I,
)
META_ROW = re.compile(
    r"^\|\s*[`*]*(id|title|slug|sp|sp_estimated|depends_on|depends|depends on|status|plan|file"
    r"|key|field)[`*]*\s*\|\s*(.*?)\s*\|$",
    re.I,
)
TABLE_RULE = re.compile(r"\|[-| :]+\|")
SP_TEXT = re.compile(r"\b(?:SP|sp|story points)\**\s*[:=]?\s*\**\s*(\d+)\b")
TITLE_TEXT = re.compile(r"^(?:Milestone\s+)?M0*\d+\s*[—–:\-]\s*(.+)$")
PROSE_DEPENDS = re.compile(r"\bM0*(\d+)\s+(?:needs|depends on|requires)\s+([^;.]*)")
MILESTONE_REF = re.compile(r"M0*(\d+)")
OVERVIEW_HEADING = re.compile(r"#{1,3}\s+Milestones")

PLAN = "plan"
OVERVIEW = "overview"
MARKER = "marker"


@dataclass(frozen=True)
class Milestone:
    id: str
    title: str
    slug: str
    sp: int | None
    depends_on: tuple[str, ...]
    sections: Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class Cut:
    plan_lines: tuple[str, ...]
    overview_lines: tuple[str, ...]
    marker_lines: tuple[str, ...]
    milestones: tuple[Milestone, ...]
    groups: tuple[tuple[str, ...], ...]
    flags: tuple[str, ...]
    demoted: int
    # Index into plan_lines where the generated milestone block goes: where the
    # draft's overview stood, else before the first milestone.
    generated_at: int = 0


@dataclass
class _Block:
    start: int
    source_id: int
    level: int
    heads: list[tuple[int, int, str]] = field(default_factory=lambda: [])
    end: int = 0


def split_lines(text: str) -> list[str]:
    """Lines split on ``\\n`` only, each keeping its ending."""
    return [line for line in re.split(r"(?<=\n)", text) if line]


def _bare(line: str) -> str:
    return line.rstrip("\r\n")


def section_of(text: str) -> str | None:
    return SECTION_NAMES.get(re.sub(r"[*_`:.]", "", text).strip().lower())


def kebab(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "milestone"


def is_fence(line: str) -> bool:
    return line.lstrip().startswith("```")


def _in_fence(src: Sequence[str]) -> list[bool]:
    """Per 1-based line (index 0 unused); fence lines themselves count as inside."""
    inside = [False]
    open_ = False
    for line in src:
        if is_fence(line):
            inside.append(True)
            open_ = not open_
            continue
        inside.append(open_)
    return inside


def meta_row(text: str) -> bool:
    """A row of an embedded per-milestone metadata table (`| sp | 5 |`, `| key | value |`)."""
    match = META_ROW.match(text)
    if not match:
        return False
    key, value = match.group(1).lower(), match.group(2)
    if key in ("key", "field"):
        return value.lower().strip("`* ") in ("value", "")
    if key == "file":
        return "milestones/" in value
    return "|" not in value


def _meta_fences(src: Sequence[str]) -> set[int]:
    """1-based fence lines whose block holds only metadata (`---`, `key: value`, list items)."""
    out: set[int] = set()
    open_at: int | None = None
    for number, line in enumerate(src, 1):
        if not is_fence(line):
            continue
        if open_at is None:
            open_at = number
            continue
        body = [x.strip() for x in src[open_at : number - 1] if x.strip()]
        if body and all(x == "---" or META_KEY.match(x) or x.startswith("- ") for x in body):
            out.update((open_at, number))
        open_at = None
    return out


def demote(lines: Sequence[str]) -> tuple[list[str], int]:
    """`#`/`##` headings outside code fences raised to `###`, and how many were."""
    out: list[str] = []
    fence = False
    count = 0
    for line in lines:
        if is_fence(line):
            fence = not fence
        elif not fence and re.match(r"^#{1,2}\s", line):
            line = "###" + line.lstrip("#")
            count += 1
        out.append(line)
    return out, count


def block(lines: Sequence[str]) -> str:
    """Section body ending in exactly one blank line before the next heading."""
    if not lines:
        return ""
    text = "".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    if not text.endswith("\n\n"):
        text += "\n"
    return text


def _overview_table(src: Sequence[str]) -> tuple[dict[int, dict[str, object]], set[int]]:
    """Rows by source id and the overview's line numbers, from the `## Milestones` table."""
    rows: dict[int, dict[str, object]] = {}
    lines: set[int] = set()
    start = next(
        (n for n, line in enumerate(src, 1) if OVERVIEW_HEADING.fullmatch(line.strip())), None
    )
    if start is None:
        return rows, lines
    lines.add(start)
    header: list[str] | None = None
    for number in range(start + 1, len(src) + 1):
        text = src[number - 1].strip()
        if HEADING.match(text):
            break
        if not text.startswith("|"):
            if header is not None and text:
                break
            continue
        lines.add(number)
        cells = [c.strip() for c in text.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set(text) <= set("|-: "):
            continue
        match = re.fullmatch(r"\[*M?0*(\d+)\]*", cells[0].strip("`*"))
        if not match:
            continue
        row: dict[str, object] = {}
        for key, value in zip(header, cells, strict=False):
            if key in ("sp", "story points"):
                digits = re.sub(r"\D", "", value)
                row["sp"] = int(digits) if digits else None
            elif key == "title" or (key == "milestone" and header[0] != "milestone"):
                row["title"] = value
            elif key.startswith("depend"):
                row["deps"] = sorted(int(x) for x in MILESTONE_REF.findall(value))
        rows[int(match.group(1))] = row
    return rows, lines


def _meta_of(lines: Sequence[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in lines:
        match = re.match(r"^[`*]*([A-Za-z_ ]+?)[`*]*\s*:\s*[`*]*\s*(.*?)\s*$", line.strip())
        if match:
            out.setdefault(match.group(1).strip().lower().replace(" ", "_"), match.group(2))
    return out


def _blocks(src: Sequence[str], fenced: Sequence[bool], flags: list[str]) -> list[_Block]:
    blocks: list[_Block] = []
    for number, line in enumerate(src, 1):
        if fenced[number]:
            continue
        found = MILESTONE_HEADING.match(_bare(line))
        heading = HEADING.match(_bare(line))
        if not (found and heading):
            continue
        source_id = int(found.group(1) or found.group(2))
        level, text = len(heading.group(1)), heading.group(2)
        if blocks and blocks[-1].source_id == source_id:
            blocks[-1].heads.append((number, level, text))
            continue
        if any(b.source_id == source_id for b in blocks):
            flags.append(
                f"M{source_id} heading repeats at line {number}; kept in the earlier block"
            )
            blocks[-1].heads.append((number, level, text))
            continue
        blocks.append(_Block(number, source_id, level, [(number, level, text)]))
    return blocks


def _close_last(src: Sequence[str], fenced: Sequence[bool], blocks: list[_Block]) -> None:
    """Bound every block; the last ends at the first later heading as high as the bodies'
    container (`## Milestone files` above the first milestone), else as high as the
    milestone headings, that is not a section."""
    count = len(src)
    for k, b in enumerate(blocks):
        b.end = blocks[k + 1].start - 1 if k + 1 < len(blocks) else count
    milestone_level = min(b.level for b in blocks)
    end_level = milestone_level
    for number in range(blocks[0].start - 1, 0, -1):
        heading = HEADING.match(_bare(src[number - 1]))
        if heading and not fenced[number] and len(heading.group(1)) < milestone_level:
            end_level = len(heading.group(1))
            break
    last = blocks[-1]
    head_numbers = {h[0] for h in last.heads}
    for number in range(last.start + 1, count + 1):
        heading = HEADING.match(_bare(src[number - 1]))
        if fenced[number] or not heading or number in head_numbers:
            continue
        text = heading.group(2)
        if (
            len(heading.group(1)) <= end_level
            and not section_of(text)
            and re.sub(r"[*_`:.]", "", text).strip().lower() not in BLOCK_HEADINGS
        ):
            end = number - 1
            while end > last.start and src[end - 1].strip() in ("", "---"):
                end -= 1
            last.end = end
            break


def _metadata(
    src: Sequence[str], fenced: Sequence[bool], meta_fences: set[int], b: _Block
) -> tuple[set[int], list[str]]:
    """Marker line numbers of a block and its embedded `key: value` metadata lines."""
    start, end = b.start, b.end
    markers = {h[0] for h in b.heads}
    meta: list[str] = []
    j = end
    while j > start and src[j - 1].strip() in ("", "---") and not fenced[j]:
        if src[j - 1].strip() == "---":
            markers.add(j)
        j -= 1

    def after_marker(number: int) -> bool:
        k = number - 1
        while k > start and not src[k - 1].strip():
            k -= 1
        return k in markers

    i = start
    while i <= end:
        text = src[i - 1].strip()
        if i in meta_fences and text.startswith("```"):
            close = next(x for x in range(i + 1, end + 1) if x in meta_fences)
            markers.update(range(i, close + 1))
            meta += [src[x - 1] for x in range(i + 1, close)]
            i = close + 1
            continue
        if text == "---" and not fenced[i] and i - 1 in markers | {start}:
            close = next(
                (x for x in range(i + 1, min(end, i + 15) + 1) if src[x - 1].strip() == "---"),
                None,
            )
            if close and all(
                META_KEY.match(src[x - 1].strip()) or not src[x - 1].strip()
                for x in range(i + 1, close)
            ):
                markers.update(range(i, close + 1))
                meta += [src[x - 1] for x in range(i + 1, close)]
                i = close + 1
                continue
        # `sp: 3` / `depends_on: [M01]` lines opening the block, the draft's fixed format
        if META_KEY.match(text) and not fenced[i] and after_marker(i):
            markers.add(i)
            meta.append(src[i - 1])
            i += 1
            continue
        if text.startswith("|") and not fenced[i] and meta_row(text):
            close = i
            while (
                close + 1 <= end
                and src[close].strip().startswith("|")
                and (meta_row(src[close].strip()) or TABLE_RULE.fullmatch(src[close].strip()))
            ):
                close += 1
            markers.update(range(i, close + 1))
            meta += [
                re.sub(r"^\|\s*(.*?)\s*\|\s*(.*?)\s*\|$", r"\1: \2", src[x - 1].strip())
                for x in range(i, close + 1)
            ]
            i = close + 1
            continue
        i += 1
    return markers, meta


@dataclass
class _Draft:
    source_id: int
    title: str
    sp: int | None
    deps: list[int]


def _fields(
    src: Sequence[str],
    fenced: Sequence[bool],
    b: _Block,
    meta: Sequence[str],
    row: Mapping[str, object],
    new_id: str,
    flags: list[str],
) -> _Draft:
    md = _meta_of(meta)
    body = "".join(src[x - 1] for x in range(b.start, b.end + 1) if not fenced[x])
    title = md.get("title", "").strip("\"'") or str(row.get("title", ""))
    if not title:
        for _, _, text in b.heads:
            found = TITLE_TEXT.match(text.strip("` "))
            if found and "/" not in found.group(1):
                title = found.group(1).strip()
                break
    if not title:
        title = (
            re.sub(r"^.*?M0*\d+-", "", b.heads[0][2]).split("/")[0].replace("-", " ").strip("` ")
        )
        flags.append(f"M{new_id}: title taken from the path heading")
    title = title.strip("`* ")

    sp: int | None = None
    row_sp = row.get("sp")
    if re.fullmatch(r"\d+", md.get("sp", "").strip()):
        sp = int(md["sp"].strip())
    elif isinstance(row_sp, int):
        sp = row_sp
    else:
        found_sp = SP_TEXT.search(body)
        if found_sp:
            sp = int(found_sp.group(1))
    if sp is None:
        flags.append(f"M{new_id}: sp not stated anywhere; left null")

    deps: list[int] = []
    key = next((k for k in md if k.startswith("depend")), None)
    row_deps = row.get("deps")
    if key is not None:
        deps = sorted(int(x) for x in MILESTONE_REF.findall(md[key]))
    elif isinstance(row_deps, list):
        deps = [int(x) for x in row_deps]  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
    else:
        found_deps = DEPENDS_TEXT.search(body)
        if found_deps:
            deps = sorted(
                int(x) for x in MILESTONE_REF.findall(re.split(r"[·]", found_deps.group(1))[0])
            )
    return _Draft(b.source_id, title, sp, [d for d in deps if d != b.source_id])


def _prose_deps(src: Sequence[str], drafts: Sequence[_Draft]) -> None:
    """`M4 needs M1 (...)` prose, read only when nothing structured states a dependency."""
    if any(d.deps for d in drafts):
        return
    for line in src:
        for mid, rest in PROSE_DEPENDS.findall(line):
            rest = re.split(r",?\s+and,? for its", re.sub(r"\([^)]*\)", "", rest))[0]
            for d in drafts:
                if d.source_id == int(mid):
                    named = {int(x) for x in MILESTONE_REF.findall(rest)}
                    d.deps = sorted((set(d.deps) | named) - {int(mid)})


def group(milestones: Sequence[Milestone], max_sp: int | None) -> list[tuple[str, ...]]:
    """Contiguous runs in id order while the summed sp stays at or under `max_sp`; a lone
    milestone is always a valid group; `max_sp=None` puts each in its own."""
    if max_sp is None:
        return [(m.id,) for m in milestones]
    groups: list[tuple[str, ...]] = []
    current: list[str] = []
    total = 0
    for m in milestones:
        sp = m.sp or 0
        if current and total + sp > max_sp:
            groups.append(tuple(current))
            current, total = [], 0
        current.append(m.id)
        total += sp
    if current:
        groups.append(tuple(current))
    return groups


def cut_draft(text: str, max_sp: int | None) -> Cut:
    src = split_lines(text)
    count = len(src)
    fenced = _in_fence(src)
    flags: list[str] = []
    blocks = _blocks(src, fenced, flags)
    if not blocks:
        return Cut(tuple(src), (), (), (), (), tuple(flags), 0, len(src))
    _close_last(src, fenced, blocks)

    owner: dict[int, str] = {}
    rows, overview = _overview_table(src)
    first, last = blocks[0], blocks[-1]
    for number in range(1, first.start):
        owner[number] = OVERVIEW if number in overview else PLAN
    for number in range(last.end + 1, count + 1):
        owner[number] = PLAN

    meta_fences = _meta_fences(src)
    drafts: list[_Draft] = []
    for k, b in enumerate(blocks, 1):
        new_id = f"{k:02d}"
        markers, meta = _metadata(src, fenced, meta_fences, b)
        section = "tasks"
        for number in range(b.start, b.end + 1):
            if number in markers:
                owner[number] = MARKER
                continue
            heading = HEADING.match(_bare(src[number - 1])) if not fenced[number] else None
            named = section_of(heading.group(2)) if heading else None
            if named:
                section = named
                owner[number] = MARKER
                continue
            if not src[number - 1].strip() and number > b.start and owner.get(number - 1) == MARKER:
                owner[number] = MARKER
                continue
            owner[number] = f"{new_id}.{section}"
        drafts.append(_fields(src, fenced, b, meta, rows.get(b.source_id, {}), new_id, flags))

    _prose_deps(src, drafts)
    to_new = {d.source_id: f"{k:02d}" for k, d in enumerate(drafts, 1)}
    milestones: list[Milestone] = []
    demoted = 0
    for k, d in enumerate(drafts, 1):
        new_id = f"{k:02d}"
        unknown = [x for x in d.deps if x not in to_new]
        if unknown:
            flags.append(f"M{new_id}: depends on unknown {', '.join(f'M{x}' for x in unknown)}")
        later = sorted(to_new[x] for x in d.deps if x in to_new and to_new[x] > new_id)
        if later:
            flags.append(f"M{new_id}: depends on later {', '.join(f'M{x}' for x in later)}")
        sections: dict[str, tuple[str, ...]] = {}
        for key in SECTION_KEYS:
            lines = tuple(src[n - 1] for n in range(1, count + 1) if owner[n] == f"{new_id}.{key}")
            sections[key] = lines
            if sum(is_fence(line) for line in lines) % 2:
                flags.append(f"M{new_id}: {key} has an unbalanced code fence")
            demoted += demote(lines)[1]
        milestones.append(
            Milestone(
                id=new_id,
                title=d.title,
                slug=kebab(d.title),
                sp=d.sp,
                depends_on=tuple(sorted(to_new[x] for x in d.deps if x in to_new)),
                sections=sections,
            )
        )

    overview_numbers = [n for n in range(1, count + 1) if owner[n] == OVERVIEW]
    anchor = (
        overview_numbers[0]
        if overview_numbers
        else min(n for n in range(1, count + 1) if owner[n] not in (PLAN, OVERVIEW))
    )
    return Cut(
        plan_lines=tuple(src[n - 1] for n in range(1, count + 1) if owner[n] == PLAN),
        overview_lines=tuple(src[n - 1] for n in overview_numbers),
        marker_lines=tuple(src[n - 1] for n in range(1, count + 1) if owner[n] == MARKER),
        milestones=tuple(milestones),
        groups=tuple(group(milestones, max_sp)),
        flags=tuple(flags),
        demoted=demoted,
        generated_at=sum(1 for n in range(1, anchor) if owner[n] == PLAN),
    )
