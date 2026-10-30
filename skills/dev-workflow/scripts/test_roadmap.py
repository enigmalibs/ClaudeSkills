"""Tests for roadmap.py — run: python3 -B -m unittest discover -s <this directory>"""

import contextlib
import io
import itertools
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True  # keep the skill directory free of __pycache__
sys.path.insert(0, str(Path(__file__).resolve().parent))
import roadmap  # noqa: E402

RAGGED = """# Roadmap

Intro text stays as is.

| ID | Title | Status | Plan |
|---|---|---|---|
| FEATURE-3A7F | User authentication | TODO | docs/plan/FEATURE-3A7F.md |
| - PHASE01 | Login flow | TODO | (in FEATURE-3A7F.md) |
| - PHASE02 | OAuth providers | TODO | (in FEATURE-3A7F.md) |
| BUG-9C2E | Fix token refresh — `retry` | DONE | docs/plan/BUG-9C2E.md |

> `FEATURE-0000` footnote stays as is.
"""

TABLE_ONLY = RAGGED[:RAGGED.index("\n> ")]

PLAN_MULTI = """# FEATURE-3A7F — User authentication

**Status:** TODO
**Type:** FEATURE (multi-phase)
**Run:** feature/2026-09-10-user-auth

## PHASE01 — Login flow

**Status:** TODO

## PHASE02 — OAuth providers

**Status:** TODO
"""

PLAN_SINGLE = "# BUG-9C2E — Fix token refresh\n\n**Status:** DONE\n**Type:** BUG\n"


def phased_roadmap(base_status, *phase_statuses):
    """A roadmap holding only FEATURE-3A7F, with one phase row per status."""
    rows = [f"| FEATURE-3A7F | User authentication | {base_status} | docs/plan/FEATURE-3A7F.md |"]
    rows += [f"| - PHASE{n:02d} | Phase {n} | {s} | (in FEATURE-3A7F.md) |" for n, s in enumerate(phase_statuses, 1)]
    return "| ID | Title | Status | Plan |\n|---|---|---|---|\n" + "\n".join(rows) + "\n"


class Project:
    """A throwaway project root with docs/roadmap.md and docs/plan/."""

    def __init__(self, roadmap_text=RAGGED, plans=None):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "docs" / "plan").mkdir(parents=True)
        self.write("docs/roadmap.md", roadmap_text)
        for name, text in (plans if plans is not None else
                           {"FEATURE-3A7F": PLAN_MULTI, "BUG-9C2E": PLAN_SINGLE}).items():
            self.write(f"docs/plan/{name}.md", text)

    def write(self, rel, text, newline="\n", bom=False):
        data = text.replace("\n", newline).encode("utf-8")
        (self.root / rel).write_bytes(b"\xef\xbb\xbf" + data if bom else data)

    def read(self, rel):
        return (self.root / rel).read_bytes()

    def text(self, rel):
        return self.read(rel).decode("utf-8-sig")

    def run(self, *argv):
        return self.call([argv[0], "--root", str(self.root), *argv[1:]])

    def call(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = roadmap.main(argv)
        return code, out.getvalue(), err.getvalue()

    def close(self):
        self._tmp.cleanup()


def table_lines(text):
    return [l for l in text.splitlines() if l.startswith("|")]


class ProjectTest(unittest.TestCase):
    def setUp(self):
        self.p = Project()

    def tearDown(self):
        self.p.close()


class FmtTests(ProjectTest):
    def test_pads_every_column_to_its_widest_cell(self):
        code, _, _ = self.p.run("fmt")
        self.assertEqual(code, 0)
        lines = table_lines(self.p.text("docs/roadmap.md"))
        self.assertEqual(len({len(l) for l in lines}), 1, lines)
        self.assertEqual(lines[1], "|" + "|".join("-" * (w + 2) for w in (12, 27, 6, 25)) + "|")

    def test_counts_characters_not_bytes(self):
        self.p.run("fmt")
        row = next(l for l in table_lines(self.p.text("docs/roadmap.md")) if l.startswith("| BUG"))
        self.assertIn("| Fix token refresh — `retry` | DONE   |", row)

    def test_is_idempotent(self):
        self.p.run("fmt")
        once = self.p.read("docs/roadmap.md")
        code, out, _ = self.p.run("fmt")
        self.assertEqual((code, self.p.read("docs/roadmap.md")), (0, once))
        self.assertIn("already formatted", out)

    def test_leaves_text_and_footnotes_untouched(self):
        self.p.run("fmt")
        text = self.p.text("docs/roadmap.md")
        self.assertTrue(text.startswith("# Roadmap\n\nIntro text stays as is.\n\n"))
        self.assertTrue(text.endswith("\n\n> `FEATURE-0000` footnote stays as is.\n"))

    def test_check_reports_without_writing(self):
        before = self.p.read("docs/roadmap.md")
        code, _, err = self.p.run("fmt", "--check")
        self.assertEqual((code, self.p.read("docs/roadmap.md")), (1, before))
        self.assertIn("not aligned", err)

    def test_preserves_crlf_and_bom(self):
        self.p.write("docs/roadmap.md", RAGGED, newline="\r\n", bom=True)
        self.p.run("fmt")
        raw = self.p.read("docs/roadmap.md")
        self.assertTrue(raw.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))

    def test_rewrites_a_mixed_endings_file_entirely_as_crlf(self):
        self.p.write("docs/roadmap.md", RAGGED.replace("\n", "\r\n", 2))
        self.p.run("fmt")
        raw = self.p.read("docs/roadmap.md")
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))
        self.assertEqual(raw.count(b"\r\n"), RAGGED.count("\n"))

    def test_root_is_accepted_before_the_subcommand(self):
        code, out, _ = self.p.call(["--root", str(self.p.root), "fmt"])
        self.assertEqual(code, 0)
        self.assertIn("re-padded", out)
        self.assertEqual(self.p.run("fmt", "--check")[0], 0)

    def test_refuses_a_file_without_the_registry_table(self):
        self.p.write("docs/roadmap.md", "# Roadmap\n\nNo table.\n")
        code, _, err = self.p.run("fmt")
        self.assertEqual(code, 1)
        self.assertIn("no '| ID | Title | Status | Plan |' table", err)


class SetStatusTests(ProjectTest):
    def test_repads_when_a_wider_status_first_appears(self):
        self.p.run("fmt")
        code, _, _ = self.p.run("set-status", "FEATURE-3A7F-PHASE01", "IN", "PROGRESS")
        self.assertEqual(code, 0)
        lines = table_lines(self.p.text("docs/roadmap.md"))
        self.assertEqual(len({len(l) for l in lines}), 1, lines)
        self.assertRegex("\n".join(lines), r"\| - PHASE01 +\| Login flow +\| IN PROGRESS \|")

    def test_phase_flip_updates_the_plan_section_and_cascades_to_the_base(self):
        self.p.run("set-status", "FEATURE-3A7F-PHASE01", "IN PROGRESS")
        plan = self.p.text("docs/plan/FEATURE-3A7F.md")
        self.assertIn("## PHASE01 — Login flow\n\n**Status:** IN PROGRESS", plan)
        self.assertIn("## PHASE02 — OAuth providers\n\n**Status:** TODO", plan)
        self.assertTrue(plan.startswith("# FEATURE-3A7F — User authentication\n\n**Status:** IN PROGRESS\n"))
        self.assertRegex(self.p.text("docs/roadmap.md"), r"\| FEATURE-3A7F \| User authentication +\| IN PROGRESS \|")

    def test_final_phase_done_flips_the_base_done(self):
        self.p.run("set-status", "FEATURE-3A7F-PHASE01", "DONE")
        self.assertIn("IN PROGRESS", self.p.text("docs/plan/FEATURE-3A7F.md").splitlines()[2])
        self.p.run("set-status", "FEATURE-3A7F-PHASE02", "DONE")
        plan = self.p.text("docs/plan/FEATURE-3A7F.md")
        self.assertEqual(plan.count("**Status:** DONE"), 3)
        self.assertRegex(self.p.text("docs/roadmap.md"), r"\| FEATURE-3A7F \| User authentication +\| DONE +\|")

    def test_single_phase_item(self):
        code, out, _ = self.p.run("set-status", "BUG-9C2E", "in_progress")
        self.assertEqual(code, 0)
        self.assertIn("BUG-9C2E: DONE -> IN PROGRESS", out)
        self.assertIn("**Status:** IN PROGRESS\n**Type:** BUG", self.p.text("docs/plan/BUG-9C2E.md"))

    def base_status(self):
        row = next(l for l in table_lines(self.p.text("docs/roadmap.md")) if l.startswith("| FEATURE-3A7F"))
        header = self.p.text("docs/plan/FEATURE-3A7F.md").splitlines()[2]
        return row.split("|")[3].strip(), header

    def test_every_phase_terminal_with_one_done_flips_the_base_done(self):
        for flips in ((("PHASE01", "ABANDONED"), ("PHASE02", "DONE")),
                      (("PHASE01", "DONE"), ("PHASE02", "ABANDONED"))):
            with self.subTest(flips=flips):
                self.p.close()
                self.p = Project()
                for phase, status in flips:
                    self.p.run("set-status", f"FEATURE-3A7F-{phase}", status)
                self.assertEqual(self.base_status(), ("DONE", "**Status:** DONE"))

    def test_every_phase_abandoned_flips_the_base_abandoned(self):
        self.p.run("set-status", "FEATURE-3A7F-PHASE01", "ABANDONED")
        code, out, _ = self.p.run("set-status", "FEATURE-3A7F-PHASE02", "ABANDONED")
        self.assertEqual(code, 0)
        self.assertIn("FEATURE-3A7F: TODO -> ABANDONED", out)
        self.assertEqual(self.base_status(), ("ABANDONED", "**Status:** ABANDONED"))

    def test_an_abandoned_phase_with_work_left_leaves_the_base_unchanged(self):
        self.p.run("set-status", "FEATURE-3A7F-PHASE01", "ABANDONED")
        self.assertEqual(self.base_status(), ("TODO", "**Status:** TODO"))
        self.p.write("docs/roadmap.md", phased_roadmap("IN PROGRESS", "DONE", "TODO", "TODO"))
        self.p.write("docs/plan/FEATURE-3A7F.md", PLAN_MULTI.replace("**Status:** TODO", "**Status:** IN PROGRESS", 1))
        self.p.run("set-status", "FEATURE-3A7F-PHASE02", "ABANDONED")
        self.assertEqual(self.base_status(), ("IN PROGRESS", "**Status:** IN PROGRESS"))

    def test_abandoning_a_multi_phase_item_abandons_its_open_phases(self):
        self.p.write("docs/roadmap.md", phased_roadmap("IN PROGRESS", "IN PROGRESS", "TODO"))
        self.p.write("docs/plan/FEATURE-3A7F.md", PLAN_MULTI.replace("**Status:** TODO", "**Status:** IN PROGRESS", 2))
        code, out, _ = self.p.run("set-status", "FEATURE-3A7F", "ABANDONED")
        self.assertEqual(code, 0)
        self.assertIn("FEATURE-3A7F-PHASE01: IN PROGRESS -> ABANDONED", out)
        self.assertIn("FEATURE-3A7F-PHASE02: TODO -> ABANDONED", out)
        self.assertEqual(self.base_status(), ("ABANDONED", "**Status:** ABANDONED"))
        self.assertEqual(self.p.text("docs/plan/FEATURE-3A7F.md").count("**Status:** ABANDONED"), 3)
        self.assertEqual([l.split("|")[3].strip() for l in table_lines(self.p.text("docs/roadmap.md"))[2:]],
                         ["ABANDONED"] * 3)

    def test_abandoning_an_item_with_a_done_phase_keeps_it_and_the_item_follows_to_done(self):
        self.p.write("docs/roadmap.md", phased_roadmap("IN PROGRESS", "DONE", "TODO"))
        self.p.write("docs/plan/FEATURE-3A7F.md", PLAN_MULTI.replace("**Status:** TODO", "**Status:** IN PROGRESS", 1)
                     .replace("Login flow\n\n**Status:** TODO", "Login flow\n\n**Status:** DONE"))
        code, out, _ = self.p.run("set-status", "FEATURE-3A7F", "ABANDONED")
        self.assertEqual(code, 0)
        self.assertNotIn("PHASE01:", out)
        self.assertIn("FEATURE-3A7F-PHASE02: TODO -> ABANDONED", out)
        self.assertIn("FEATURE-3A7F: IN PROGRESS -> DONE", out)
        self.assertIn("the item follows its phases to DONE", out)
        self.assertEqual(self.base_status(), ("DONE", "**Status:** DONE"))
        plan = self.p.text("docs/plan/FEATURE-3A7F.md")
        self.assertIn("## PHASE01 — Login flow\n\n**Status:** DONE", plan)
        self.assertIn("## PHASE02 — OAuth providers\n\n**Status:** ABANDONED", plan)

    def test_a_multi_phase_item_refuses_every_other_status(self):
        for status in ("TODO", "IN PROGRESS", "DONE"):
            with self.subTest(status=status):
                self.assertNothingWritten("set-status", "FEATURE-3A7F", status,
                                          message="flip the phases — the item follows them")

    def test_abandoning_an_item_with_no_open_phase_writes_nothing(self):
        self.p.write("docs/roadmap.md", phased_roadmap("DONE", "DONE", "ABANDONED"))
        self.assertNothingWritten("set-status", "FEATURE-3A7F", "ABANDONED", message="no open phase to abandon")

    def test_replaces_a_quarantine_note_with_the_bare_status(self):
        self.p.write("docs/plan/BUG-9C2E.md", "# BUG-9C2E\n\n**Status:** IN PROGRESS — quarantined by x: red\n")
        self.p.run("set-status", "BUG-9C2E", "DONE")
        self.assertIn("**Status:** DONE\n", self.p.text("docs/plan/BUG-9C2E.md"))

    def assertNothingWritten(self, *argv, message):
        before = (self.p.read("docs/roadmap.md"), self.p.read("docs/plan/FEATURE-3A7F.md"))
        code, _, err = self.p.run(*argv)
        self.assertEqual(code, 1)
        self.assertIn(message, err)
        self.assertEqual((self.p.read("docs/roadmap.md"), self.p.read("docs/plan/FEATURE-3A7F.md")), before)

    def test_unknown_id_writes_nothing(self):
        self.assertNothingWritten("set-status", "FEATURE-FFFF", "DONE", message="not in")

    def test_unknown_phase_writes_nothing(self):
        self.assertNothingWritten("set-status", "FEATURE-3A7F-PHASE09", "DONE", message="has no PHASE09 row")

    def test_unknown_status_writes_nothing(self):
        self.assertNothingWritten("set-status", "FEATURE-3A7F-PHASE01", "STARTED", message="unknown status")

    def test_plan_without_a_status_line_writes_nothing(self):
        self.p.write("docs/plan/FEATURE-3A7F.md", "# FEATURE-3A7F\n\n## PHASE01 — Login flow — **TODO**\n")
        self.assertNothingWritten("set-status", "FEATURE-3A7F-PHASE01", "DONE", message="legacy")

    def test_missing_plan_file_writes_nothing(self):
        (self.p.root / "docs/plan/BUG-9C2E.md").unlink()
        before = self.p.read("docs/roadmap.md")
        code, _, err = self.p.run("set-status", "BUG-9C2E", "TODO")
        self.assertEqual((code, self.p.read("docs/roadmap.md")), (1, before))
        self.assertIn("no such file", err)


class AddTests(ProjectTest):
    def test_appends_the_item_and_its_phases_at_the_bottom(self):
        code, _, _ = self.p.run("add", "CODE-REVIEW-7F10", "PR #42 review",
                                "--phase", "[Critical] SQLi in Order", "--phase", "[Medium] N+1 in Listing")
        self.assertEqual(code, 0)
        lines = table_lines(self.p.text("docs/roadmap.md"))
        self.assertEqual(len({len(l) for l in lines}), 1)
        self.assertEqual([l.split("|")[1].strip() for l in lines[-3:]],
                         ["CODE-REVIEW-7F10", "- PHASE01", "- PHASE02"])
        self.assertIn("| docs/plan/CODE-REVIEW-7F10.md |", lines[-3])
        self.assertIn("(in CODE-REVIEW-7F10.md)", lines[-1])

    def test_build_flow_starts_the_item_and_its_first_phase_in_progress(self):
        self.p.run("add", "FEATURE-1234", "New thing", "--phase", "One", "--phase", "Two", "--status", "IN PROGRESS")
        rows = [l.split("|")[3].strip() for l in table_lines(self.p.text("docs/roadmap.md"))[-3:]]
        self.assertEqual(rows, ["IN PROGRESS", "IN PROGRESS", "TODO"])

    def test_refuses_a_duplicate(self):
        code, _, err = self.p.run("add", "BUG-9C2E", "Again")
        self.assertEqual(code, 1)
        self.assertIn("already in", err)

    def test_refuses_a_phase_id_and_a_finished_status(self):
        self.assertEqual(self.p.run("add", "BUG-1111-PHASE01", "x")[0], 1)
        self.assertEqual(self.p.run("add", "BUG-1111", "x", "--status", "DONE")[0], 1)

    def test_a_pipe_in_a_title_is_escaped_and_keeps_the_row_at_four_cells(self):
        self.p.write("docs/plan/BUG-1111.md", "# BUG-1111\n\n**Status:** TODO\n")
        self.assertEqual(self.p.run("add", "BUG-1111", "Parse a | b")[0], 0)
        self.assertEqual(self.p.run("fmt", "--check")[0], 0)
        code, out, _ = self.p.run("set-status", "BUG-1111", "DONE")
        self.assertEqual(code, 0, out)
        row = table_lines(self.p.text("docs/roadmap.md"))[-1]
        self.assertRegex(row, r"^\| BUG-1111 +\| Parse a \\\| b +\| DONE +\| docs/plan/BUG-1111.md +\|$")

    def test_warns_about_a_long_title(self):
        code, _, err = self.p.run("add", "BUG-1111", "x" * 41)
        self.assertEqual(code, 0)
        self.assertIn("over 40 characters", err)


class NewIdTests(ProjectTest):
    def test_regenerates_on_a_same_type_collision(self):
        (self.p.root / "docs/plan/FEATURE-00AA.md").write_text("# stray\n", encoding="utf-8")
        draws = iter([0x3A7F, 0x00AA, 0x9C2E])  # roadmap row, stray plan file, then free
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            new = roadmap.cmd_new_id(self.p.root, "FEATURE", rng=lambda _: next(draws))
        self.assertEqual(new, "FEATURE-9C2E")  # BUG-9C2E exists, but uniqueness is per type
        self.assertIn("docs/plan/FEATURE-00AA.md has no roadmap row", err.getvalue())

    def test_never_returns_an_existing_id(self):
        for plan in (self.p.root / "docs/plan").glob("*.md"):
            plan.unlink()
        existing = {f"FEATURE-{n:04X}" for n in range(0, 65536, 2)}  # every other ID taken: ~1 in 2 draws collide
        rows = "\n".join(f"| {i} | t | DONE | docs/plan/{i}.md |" for i in sorted(existing))
        self.p.write("docs/roadmap.md", "| ID | Title | Status | Plan |\n|---|---|---|---|\n" + rows + "\n")
        for _ in range(50):
            new = roadmap.cmd_new_id(self.p.root, "FEATURE")
            self.assertNotIn(new, existing)
            self.assertRegex(new, r"^FEATURE-[0-9A-F]{4}$")

    def test_works_before_any_roadmap_exists(self):
        empty = Path(tempfile.mkdtemp())
        self.assertRegex(roadmap.cmd_new_id(empty, "CODE-REVIEW"), r"^CODE-REVIEW-[0-9A-F]{4}$")


class ShowAndProgressTests(ProjectTest):
    def test_plain_show_prints_the_aligned_table_and_nothing_else(self):
        code, out, _ = self.p.run("show")
        self.assertEqual(code, 0)
        self.p.run("fmt")
        self.assertEqual(out.splitlines(), table_lines(self.p.text("docs/roadmap.md")))
        self.assertNotIn("←", out)

    def test_show_next_marks_the_recommended_item_and_its_next_phase(self):
        self.p.run("set-status", "FEATURE-3A7F-PHASE01", "DONE")
        _, out, _ = self.p.run("show", "--next")
        marked = [l for l in out.splitlines() if "←" in l]
        self.assertEqual(len(marked), 2)
        self.assertTrue(marked[0].startswith("| FEATURE-3A7F") and marked[0].endswith("  ← recommended"))
        self.assertTrue(marked[1].startswith("| - PHASE02") and marked[1].endswith("  ← next"))

    def test_show_prefers_in_progress_over_an_earlier_todo(self):
        self.p.run("set-status", "BUG-9C2E", "IN PROGRESS")
        _, out, _ = self.p.run("show", "--next")
        self.assertTrue(next(l for l in out.splitlines() if "←" in l).startswith("| BUG-9C2E"))

    def test_show_says_when_nothing_is_buildable(self):
        self.p.run("set-status", "FEATURE-3A7F-PHASE01", "DONE")
        self.p.run("set-status", "FEATURE-3A7F-PHASE02", "DONE")
        _, out, _ = self.p.run("show", "--next")
        self.assertIn("Nothing to build", out)
        self.assertNotIn("←", out)

    def test_an_abandoned_item_leaves_no_phase_to_build(self):
        self.p.run("set-status", "FEATURE-3A7F", "ABANDONED")
        self.assertEqual(self.marked_phases(), (None, None))
        self.assertIn("Nothing to build", self.p.run("show", "--next")[1])

    def test_progress_table(self):
        self.p.run("set-status", "FEATURE-3A7F-PHASE01", "DONE")
        _, out, _ = self.p.run("progress", "FEATURE-3A7F")
        self.assertEqual(out.splitlines(), [
            "FEATURE-3A7F — User authentication",
            "",
            "| Phase   | Title           | Status      |",
            "|---------|-----------------|-------------|",
            "| PHASE01 | Login flow      | DONE        |",
            "| PHASE02 | OAuth providers | TODO (next) |",
        ])

    def marked_phases(self):
        """(phase marked by show --next, phase marked by progress); None when a command marks none."""
        _, show, _ = self.p.run("show", "--next")
        _, progress, _ = self.p.run("progress", "FEATURE-3A7F")
        by_show = next((l.split("|")[1].strip()[2:] for l in show.splitlines() if l.endswith("← next")), None)
        by_progress = next((l.split("|")[1].strip() for l in progress.splitlines() if "(next)" in l), None)
        return by_show, by_progress

    def test_an_in_progress_phase_in_the_middle_is_next_for_both(self):
        self.p.write("docs/roadmap.md", phased_roadmap("IN PROGRESS", "DONE", "IN PROGRESS", "TODO"))
        self.assertEqual(self.marked_phases(), ("PHASE02", "PHASE02"))
        self.assertIn("| PHASE02 | Phase 2 | IN PROGRESS (next) |", self.p.run("progress", "FEATURE-3A7F")[1])

    def test_show_next_and_progress_mark_the_same_phase_for_every_status_combination(self):
        for statuses in itertools.product(roadmap.STATUSES, repeat=3):
            with self.subTest(statuses=statuses):
                self.p.write("docs/roadmap.md", phased_roadmap("IN PROGRESS", *statuses))
                expected = next((f"PHASE{n:02d}" for n, s in enumerate(statuses, 1)
                                 if s not in ("DONE", "ABANDONED")), None)
                self.assertEqual(self.marked_phases(), (expected, expected))

    def test_progress_refuses_a_single_phase_item(self):
        self.assertEqual(self.p.run("progress", "BUG-9C2E")[0], 1)


class NoteTests(ProjectTest):
    def below_table(self):
        text = self.p.text("docs/roadmap.md")
        return text[text.rindex("|\n") + 2:]

    def test_adds_the_first_note_beneath_the_table_and_keeps_the_text_below_apart(self):
        self.p.write("docs/roadmap.md", TABLE_ONLY + "\nClosing text.\n")
        code, out, _ = self.p.run("note", "BUG-9C2E", "abandoned — superseded; replaced by `BUG-1111`.")
        self.assertEqual(code, 0)
        self.assertIn("BUG-9C2E: note added", out)
        self.assertEqual(self.below_table(),
                         "\n> `BUG-9C2E` abandoned — superseded; replaced by `BUG-1111`.\n\nClosing text.\n")

    def test_appends_after_the_last_note_one_blank_line_apart_keyed_by_a_phase_id(self):
        self.p.run("note", "BUG-9C2E", "first")
        self.p.run("note", "FEATURE-3A7F-PHASE02", "second")
        self.assertEqual(self.below_table(), "\n> `FEATURE-0000` footnote stays as is.\n"
                                             "\n> `BUG-9C2E` first\n"
                                             "\n> `FEATURE-3A7F-PHASE02` second\n")

    def test_replaces_a_note_in_place_with_its_continuation_lines_and_an_exact_key(self):
        self.p.write("docs/roadmap.md", TABLE_ONLY + "\n> `FEATURE-3A7F` old reason,\n> continued.\n"
                                                     "\n> `FEATURE-3A7F-PHASE01` phase note\n")
        code, out, _ = self.p.run("note", "FEATURE-3A7F", "new reason")
        self.assertEqual(code, 0)
        self.assertIn("note replaced", out)
        self.assertEqual(self.below_table(), "\n> `FEATURE-3A7F` new reason\n\n> `FEATURE-3A7F-PHASE01` phase note\n")

    def test_remove_undoes_an_add_byte_for_byte(self):
        for before in (RAGGED, TABLE_ONLY, TABLE_ONLY + "\nClosing text.\n"):
            with self.subTest(before=before[-30:]):
                self.p.write("docs/roadmap.md", before)
                self.p.run("fmt")
                formatted = self.p.read("docs/roadmap.md")
                self.p.run("note", "BUG-9C2E", "x")
                code, out, _ = self.p.run("note", "--remove", "BUG-9C2E")
                self.assertEqual((code, self.p.read("docs/roadmap.md")), (0, formatted))
                self.assertIn("BUG-9C2E: note removed", out)

    def test_remove_keeps_the_notes_around_it_apart(self):
        for full_id in ("FEATURE-3A7F", "BUG-9C2E", "FEATURE-3A7F-PHASE01"):
            self.p.run("note", full_id, full_id.lower())
        self.p.run("note", "--remove", "BUG-9C2E")
        self.assertEqual(self.below_table(), "\n> `FEATURE-0000` footnote stays as is.\n"
                                             "\n> `FEATURE-3A7F` feature-3a7f\n"
                                             "\n> `FEATURE-3A7F-PHASE01` feature-3a7f-phase01\n")

    def assertRefused(self, *argv, message):
        before = self.p.read("docs/roadmap.md")
        code, _, err = self.p.run(*argv)
        self.assertEqual((code, self.p.read("docs/roadmap.md")), (1, before))
        self.assertIn(message, err)

    def test_an_id_not_in_the_table_writes_nothing(self):
        self.assertRefused("note", "FEATURE-0000", "x", message="not in")
        self.assertRefused("note", "FEATURE-3A7F-PHASE09", "x", message="has no PHASE09 row")
        self.assertRefused("note", "--remove", "FEATURE-0000", message="not in")

    def test_refuses_a_missing_note_and_malformed_text(self):
        self.assertRefused("note", "--remove", "BUG-9C2E", message="no note beneath the table")
        self.assertRefused("note", "BUG-9C2E", message="needs its TEXT")
        self.assertRefused("note", "BUG-9C2E", "  ", message="needs its TEXT")
        self.assertRefused("note", "BUG-9C2E", "two\nlines", message="one line")
        self.assertRefused("note", "--remove", "BUG-9C2E", "x", message="takes no TEXT")


if __name__ == "__main__":
    unittest.main()
