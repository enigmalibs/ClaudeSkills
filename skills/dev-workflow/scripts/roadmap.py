#!/usr/bin/env python3
"""Deterministic bookkeeping for the dev-workflow roadmap (docs/roadmap.md) and plan files.

  roadmap.py [--root DIR] COMMAND ...        DIR holds docs/roadmap.md (default: the nearest one above the
                                             current directory); --root may also follow the COMMAND
  fmt [--check]                             re-pad the registry table
  set-status ID STATUS                       flip a row and its plan file's **Status:** line, then fmt
  add ID TITLE [--phase TITLE]... [--status S]
                                             append an item (and its phase rows), then fmt
  new-id TYPE                                print a fresh, collision-checked work-item ID
  show [--next]                              print the table (--next marks the recommended build)
  progress BASE_ID                           print a multi-phase item's progress table
  note ID TEXT                               add or replace the ID's footnote beneath the table: > `ID` TEXT
  note --remove ID                           remove the ID's footnote

Standard library only; runs on Linux, macOS and Windows. Exit 0 = done, 1 = refused (nothing written).
"""

import argparse
import re
import secrets
import sys
from pathlib import Path

STATUSES = ("TODO", "IN PROGRESS", "DONE", "ABANDONED")
TERMINAL = ("DONE", "ABANDONED")
TYPES = ("FEATURE", "BUG", "CODE-REVIEW")
HEADER = ["ID", "Title", "Status", "Plan"]
BASE_ID = re.compile(r"^(?:FEATURE|BUG|CODE-REVIEW)-[0-9A-F]{4}$")
FULL_ID = re.compile(r"^((?:FEATURE|BUG|CODE-REVIEW)-[0-9A-F]{4})(?:-(PHASE\d{2}))?$")
PHASE_CELL = re.compile(r"^- PHASE\d{2}$")
DELIMITER = re.compile(r"^\|[\s:|-]+\|$")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
STATUS_LINE = re.compile(r"^(\*\*Status:\*\*)([ \t]*)(.*?)([ \t]*)$")
HEADING = re.compile(r"^(#{1,6})\s")
NOTE_KEY = re.compile(r"^>\s*`([^`]+)`")
TITLE_SOFT_MAX = 40


class Refused(Exception):
    """A request the script will not apply. Nothing has been written."""


class TextFile:
    """A UTF-8 text file whose BOM and newline style survive a rewrite."""

    def __init__(self, path):
        self.path = Path(path)
        if not self.path.is_file():
            raise Refused(f"{self.path}: no such file")
        raw = self.path.read_bytes()
        self.bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")
        # Any CRLF makes the whole file CRLF on save: a mixed-endings file comes back uniformly CRLF.
        self.newline = "\r\n" if "\r\n" in text else "\n"
        self.lines = text.replace("\r\n", "\n").split("\n")

    def save(self):
        data = self.newline.join(self.lines).encode("utf-8")
        self.path.write_bytes(b"\xef\xbb\xbf" + data if self.bom else data)


def split_row(line):
    inner = line.strip()[1:-1]
    return [cell.strip() for cell in CELL_SPLIT.split(inner)]


def render_table(rows):
    """Pad every cell to its column's widest cell, header included (character count)."""
    widths = [max(len(row[c]) for row in rows) for c in range(len(rows[0]))]

    def line(row):
        return "| " + " | ".join(cell.ljust(widths[c]) for c, cell in enumerate(row)) + " |"

    return [line(rows[0]), "|" + "|".join("-" * (w + 2) for w in widths) + "|"] + [line(r) for r in rows[1:]]


def normalize_status(words):
    status = re.sub(r"[\s_-]+", " ", " ".join(words).strip()).upper()
    if status not in STATUSES:
        raise Refused(f"unknown status '{' '.join(words)}' (expected one of: {', '.join(STATUSES)})")
    return status


class Roadmap:
    """The ID · Title · Status · Plan registry table inside docs/roadmap.md."""

    def __init__(self, path):
        self.file = TextFile(path)
        lines = self.file.lines
        self.start = next((i for i, l in enumerate(lines)
                           if l.lstrip().startswith("|") and split_row(l) == HEADER), None)
        if self.start is None:
            raise Refused(f"{self.file.path}: no '| ID | Title | Status | Plan |' table")
        if self.start + 1 >= len(lines) or not DELIMITER.match(lines[self.start + 1].strip()):
            raise Refused(f"{self.file.path}:{self.start + 2}: expected the table's delimiter row")
        end = self.start + 2
        while end < len(lines) and lines[end].lstrip().startswith("|"):
            end += 1
        self.end = end
        self.rows = []
        for n, line in enumerate(lines[self.start + 2:end], self.start + 3):
            cells = split_row(line)
            if len(cells) != 4:
                raise Refused(f"{self.file.path}:{n}: expected 4 cells, found {len(cells)}")
            self.rows.append(cells)

    def render(self):
        return render_table([HEADER] + self.rows)

    def is_formatted(self):
        return self.file.lines[self.start:self.end] == self.render()

    def save(self):
        self.file.lines[self.start:self.end] = self.render()
        self.file.save()

    def items(self):
        """(item row index, [phase row indexes]) in table order."""
        out = []
        for i, row in enumerate(self.rows):
            if PHASE_CELL.match(row[0]):
                if not out:
                    raise Refused(f"{self.file.path}: phase row '{row[0]}' has no item above it")
                out[-1][1].append(i)
            else:
                out.append((i, []))
        return out

    def find(self, full_id):
        """(item index, phase indexes, phase index or None) for a base or phase ID."""
        match = FULL_ID.match(full_id)
        if not match:
            raise Refused(f"'{full_id}' is not a work-item ID (TYPE-HHHH or TYPE-HHHH-PHASENN)")
        base, phase = match.groups()
        for i, phases in self.items():
            if self.rows[i][0] != base:
                continue
            if phase is None:
                return i, phases, None
            for j in phases:
                if self.rows[j][0] == f"- {phase}":
                    return i, phases, j
            raise Refused(f"{full_id}: {base} has no {phase} row")
        raise Refused(f"{base}: not in {self.file.path}")

    def notes(self):
        """({ID: (first line, end line)}, end of the last '>' line) for the blockquote notes beneath the table.

        The region runs from the table to the first line that is neither blank nor a '>' line. A note is its
        keyed line plus any unkeyed '>' lines right below it (a hand-written multi-line note).
        """
        lines = self.file.lines
        spans, current, tail = {}, None, self.end
        for i in range(self.end, len(lines)):
            line = lines[i]
            if not line.strip():
                current = None
                continue
            if not line.startswith(">"):
                break
            tail = i + 1
            key = NOTE_KEY.match(line)
            if key:
                current = key.group(1)
                spans[current] = (i, i + 1)
            elif current is not None:
                spans[current] = (spans[current][0], i + 1)
        return spans, tail


class PlanFile:
    """docs/plan/<ID>.md — the header block's **Status:** line and one per phase section."""

    def __init__(self, path):
        self.file = TextFile(path)

    def status_index(self, phase=None):
        lines = self.file.lines
        if phase is None:
            for i, line in enumerate(lines):
                heading = HEADING.match(line)
                if heading and len(heading.group(1)) >= 2:
                    break
                if STATUS_LINE.match(line):
                    return i
            raise Refused(f"{self.file.path}: no **Status:** line in the header block")
        start = next((i for i, l in enumerate(lines)
                      if HEADING.match(l) and re.search(rf"\b{phase}\b", l)), None)
        if start is None:
            raise Refused(f"{self.file.path}: no {phase} section heading")
        level = len(HEADING.match(lines[start]).group(1))
        for i in range(start + 1, len(lines)):
            heading = HEADING.match(lines[i])
            if heading and len(heading.group(1)) <= level:
                break
            if STATUS_LINE.match(lines[i]):
                return i
        raise Refused(f"{self.file.path}: the {phase} section has no **Status:** line "
                      "(legacy status-in-heading plan: edit it by hand)")

    def set_status(self, index, status):
        m = STATUS_LINE.match(self.file.lines[index])
        self.file.lines[index] = f"{m.group(1)}{m.group(2) or ' '}{status}{m.group(4)}"


def find_root(start):
    for directory in [start, *start.parents]:
        if (directory / "docs" / "roadmap.md").is_file():
            return directory
    return None


def roadmap_path(root):
    return root / "docs" / "roadmap.md"


def cmd_fmt(root, check=False):
    roadmap = Roadmap(roadmap_path(root))
    if roadmap.is_formatted():
        return "docs/roadmap.md: already formatted"
    if check:
        raise Refused("docs/roadmap.md: the table is not aligned (run: roadmap.py fmt)")
    roadmap.save()
    return "docs/roadmap.md: table re-padded"


def cmd_set_status(root, full_id, status):
    roadmap = Roadmap(roadmap_path(root))
    item, phases, phase = roadmap.find(full_id)
    base_id = roadmap.rows[item][0]
    plan = PlanFile(root / "docs" / "plan" / f"{base_id}.md")
    changes = []  # (row index, plan section or None, new status)
    if phase is None:
        changes.append((item, None, status))
    else:
        changes.append((phase, roadmap.rows[phase][0][2:], status))
        after = [status if j == phase else roadmap.rows[j][2] for j in phases]
        base_status = roadmap.rows[item][2]
        if all(s in TERMINAL for s in after):
            final = "DONE" if "DONE" in after else "ABANDONED"
            if base_status != final:
                changes.append((item, None, final))
        elif status in ("IN PROGRESS", "DONE") and base_status == "TODO":
            changes.append((item, None, "IN PROGRESS"))
    # Locate every plan line before writing anything, so a refusal leaves both files untouched.
    plan_lines = [(plan.status_index(section), new) for _, section, new in changes]
    report = []
    for row, _, new in changes:
        old = roadmap.rows[row][2]
        label = base_id if PHASE_CELL.match(roadmap.rows[row][0]) is None else f"{base_id}-{roadmap.rows[row][0][2:]}"
        report.append(f"{label}: {old} -> {new}")
        roadmap.rows[row][2] = new
    for index, new in plan_lines:
        plan.set_status(index, new)
    plan.file.save()
    roadmap.save()
    return "\n".join(report) + "\n(roadmap row + plan file updated, table re-padded)"


def cmd_add(root, item_id, title, phase_titles, status):
    if not BASE_ID.match(item_id):
        raise Refused(f"'{item_id}' is not a base work-item ID (TYPE-HHHH)")
    if status not in ("TODO", "IN PROGRESS"):
        raise Refused("a new item starts as TODO (planning flow) or IN PROGRESS (build flow)")
    roadmap = Roadmap(roadmap_path(root))
    if any(row[0] == item_id for row in roadmap.rows):
        raise Refused(f"{item_id}: already in docs/roadmap.md")
    warnings = [f"warning: title '{t}' is over {TITLE_SOFT_MAX} characters — abbreviate it"
                for t in [title, *phase_titles] if len(t) > TITLE_SOFT_MAX]
    roadmap.rows.append([item_id, title.replace("|", "\\|"), status, f"docs/plan/{item_id}.md"])
    for n, phase_title in enumerate(phase_titles, 1):
        phase_status = "IN PROGRESS" if status == "IN PROGRESS" and n == 1 else "TODO"
        roadmap.rows.append([f"- PHASE{n:02d}", phase_title.replace("|", "\\|"), phase_status,
                             f"(in {item_id}.md)"])
    roadmap.save()
    for w in warnings:
        print(w, file=sys.stderr)
    return f"{item_id}: added at the bottom" + (f" with {len(phase_titles)} phase rows" if phase_titles else "")


def cmd_new_id(root, kind, rng=secrets.randbelow):
    path = roadmap_path(root)
    rows = Roadmap(path).rows if path.is_file() else []
    plan_dir = root / "docs" / "plan"
    plan_ids = {p.stem for p in plan_dir.glob("*.md")} if plan_dir.is_dir() else set()
    row_ids = {row[0] for row in rows}
    for stray in sorted(i for i in plan_ids - row_ids if FULL_ID.match(i)):
        print(f"warning: docs/plan/{stray}.md has no roadmap row", file=sys.stderr)
    used = {i for i in row_ids | plan_ids if i.startswith(f"{kind}-")}
    for _ in range(1000):
        candidate = f"{kind}-{rng(65536):04X}"
        if candidate not in used:
            return candidate
    raise Refused(f"no free {kind} ID after 1000 draws")


def next_phase(roadmap, phases):
    """The first phase neither DONE nor ABANDONED: the one /build resolves, show --next and progress mark."""
    return next((j for j in phases if roadmap.rows[j][2] not in TERMINAL), None)


def recommendation(roadmap):
    """(recommended item index, its next phase index) — topmost IN PROGRESS item, else topmost TODO."""
    items = roadmap.items()
    for wanted in ("IN PROGRESS", "TODO"):
        for item, phases in items:
            if roadmap.rows[item][2] == wanted:
                return item, next_phase(roadmap, phases)
    return None, None


def cmd_show(root, mark_next=False):
    roadmap = Roadmap(roadmap_path(root))
    lines = roadmap.render()
    if not mark_next:
        return "\n".join(lines)
    item, upcoming = recommendation(roadmap)
    out = lines[:2]
    for k, line in enumerate(lines[2:]):
        out.append(line + ("  ← recommended" if k == item else "  ← next" if k == upcoming else ""))
    if item is None:
        out += ["", "Nothing to build: no TODO or IN PROGRESS item."]
    return "\n".join(out)


def cmd_progress(root, base_id):
    roadmap = Roadmap(roadmap_path(root))
    item, phases, phase = roadmap.find(base_id)
    if phase is not None:
        raise Refused(f"pass the base ID, not a phase ({base_id})")
    if not phases:
        raise Refused(f"{base_id} is single-phase: it has no progress table")
    upcoming = next_phase(roadmap, phases)
    rows = [["Phase", "Title", "Status"]] + [
        [roadmap.rows[j][0][2:], roadmap.rows[j][1], roadmap.rows[j][2] + (" (next)" if j == upcoming else "")]
        for j in phases]
    return "\n".join([f"{base_id} — {roadmap.rows[item][1]}", ""] + render_table(rows))


def cmd_note(root, full_id, text, remove=False):
    roadmap = Roadmap(roadmap_path(root))
    roadmap.find(full_id)
    if remove and text is not None:
        raise Refused("note --remove takes no TEXT")
    if not remove and (text is None or not text.strip()):
        raise Refused(f"{full_id}: a note needs its TEXT (or --remove)")
    if not remove and ("\n" in text or "\r" in text):
        raise Refused(f"{full_id}: a note is one line")
    lines = roadmap.file.lines
    spans, tail = roadmap.notes()
    if remove:
        if full_id not in spans:
            raise Refused(f"{full_id}: no note beneath the table")
        start, stop = spans[full_id]
        del lines[start:stop]
        if lines[start - 1].strip() == "" and start < len(lines) and lines[start].strip() == "":
            del lines[start]
        roadmap.save()
        return f"{full_id}: note removed"
    note = f"> `{full_id}` {text.strip()}"
    if full_id in spans:
        start, stop = spans[full_id]
        lines[start:stop] = [note]
        verb = "replaced"
    else:
        lines[tail:tail] = ["", note]
        if tail + 2 < len(lines) and lines[tail + 2].strip():
            lines.insert(tail + 2, "")
        verb = "added"
    roadmap.save()
    return f"{full_id}: note {verb} beneath the table"


def build_parser():
    root_help = "project root holding docs/roadmap.md (default: nearest one above the current directory)"
    common = argparse.ArgumentParser(add_help=False)
    # SUPPRESS: a subcommand given no --root must not reset one passed before the subcommand.
    common.add_argument("--root", type=Path, default=argparse.SUPPRESS, help=root_help)
    parser = argparse.ArgumentParser(prog="roadmap.py", description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, help=root_help)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("fmt", parents=[common], help="re-pad the roadmap table")
    p.add_argument("--check", action="store_true", help="only report; exit 1 if the table is not aligned")
    p = sub.add_parser("set-status", parents=[common], help="flip a row and its plan file's status")
    p.add_argument("id")
    p.add_argument("status", nargs="+", help=" | ".join(STATUSES))
    p = sub.add_parser("add", parents=[common], help="append an item (and its phases)")
    p.add_argument("id")
    p.add_argument("title")
    p.add_argument("--phase", action="append", default=[], metavar="TITLE", help="one per phase, in order")
    p.add_argument("--status", default="TODO", help="TODO (planning flow, default) or 'IN PROGRESS' (build flow)")
    p = sub.add_parser("new-id", parents=[common], help="print a fresh work-item ID")
    p.add_argument("type", choices=TYPES)
    p = sub.add_parser("show", parents=[common], help="print the roadmap table")
    p.add_argument("--next", action="store_true", help="mark the recommended build and its next phase")
    p = sub.add_parser("progress", parents=[common], help="print a multi-phase item's progress table")
    p.add_argument("id")
    p = sub.add_parser("note", parents=[common], help="add, replace or remove an ID's footnote beneath the table")
    p.add_argument("id")
    p.add_argument("text", nargs="?", help="the note after its `ID` key; single-quote it, notes hold backticks")
    p.add_argument("--remove", action="store_true", help="remove the ID's note instead")
    return parser


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    try:
        root = args.root or find_root(Path.cwd())
        if root is None:
            if args.command != "new-id":
                raise Refused("no docs/roadmap.md in this directory or above it (pass --root)")
            root = Path.cwd()
        if args.command == "fmt":
            out = cmd_fmt(root, args.check)
        elif args.command == "set-status":
            out = cmd_set_status(root, args.id, normalize_status(args.status))
        elif args.command == "add":
            out = cmd_add(root, args.id, args.title, args.phase, normalize_status([args.status]))
        elif args.command == "new-id":
            out = cmd_new_id(root, args.type)
        elif args.command == "show":
            out = cmd_show(root, args.next)
        elif args.command == "note":
            out = cmd_note(root, args.id, args.text, args.remove)
        else:
            out = cmd_progress(root, args.id)
    except Refused as refusal:
        print(f"roadmap.py: {refusal}", file=sys.stderr)
        return 1
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
