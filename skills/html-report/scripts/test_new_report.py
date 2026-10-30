"""Tests for new_report.py — run: python3 -B -m unittest discover -s <this directory>"""

import contextlib
import datetime
import hashlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True  # keep the skill directory free of __pycache__
sys.path.insert(0, str(Path(__file__).resolve().parent))
import new_report  # noqa: E402

FRAGMENT = """<header class="doc-header">
  <h1 class="doc-title">Sample report</h1>
</header>

<article class="doc" data-numbered>
  <h2>Summary</h2>
  <p class="lead">The key message.</p>
</article>
"""

# The template's skeleton: every spot the build rewrites, and nothing else.
MINIMAL = """<!DOCTYPE html>
<html lang="en">
<head>
<title>Report Template</title>
</head>
<body id="top">
<header class="topbar"><a class="topbar__title" href="#top">Report Template</a></header>
<main id="content">
<!-- REPORT:CONTENT:START -->
<p>showcase</p>
<!-- REPORT:CONTENT:END -->
</main>
<footer class="site-footer"><span class="site-footer__title">Report Template</span>
<p>Last updated <time datetime="2026-10-30">30 October 2026</time></p></footer>
</body>
</html>
"""

# Lines of the bundled template a build may change, outside its content region.
REWRITTEN = ("<html lang=", "<title>", 'class="topbar__title"', 'class="site-footer__title"', "<time datetime=")


class Workspace(unittest.TestCase):
    """A throwaway directory holding the fragment; OUTPUT is report.html in it."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.output = self.dir / "report.html"
        self.write("content.html", FRAGMENT)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, text, newline="\n", bom=False):
        path = self.dir / name
        data = text.replace("\n", newline).encode("utf-8")
        path.write_bytes(b"\xef\xbb\xbf" + data if bom else data)
        return path

    def use_template(self, text, newline="\n"):
        """Point the script at a template of our own for the rest of the test."""
        patcher = mock.patch.object(new_report, "TEMPLATE", self.write("template.html", text, newline))
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_script(self, *extra, content="content.html", title="Sample report"):
        argv = ["-t", title, "-c", str(self.dir / content), "-o", str(self.output), *extra]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = new_report.main(argv)
        return code, out.getvalue(), err.getvalue()

    def report(self):
        return self.output.read_bytes().decode("utf-8")

    def content_region(self):
        text = self.report().replace("\r\n", "\n")
        return text[text.index(new_report.START) + len(new_report.START):text.index(new_report.END)]


class BuildTests(Workspace):
    def test_writes_the_report_and_says_so(self):
        code, out, err = self.run_script()
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out, f"new_report.py: wrote {self.output}\n")
        self.assertTrue(self.output.is_file())

    def test_replaces_the_content_region_and_keeps_the_markers(self):
        self.run_script()
        self.assertEqual(self.content_region(), "\n" + FRAGMENT.strip("\n") + "\n")
        self.assertNotIn("Template showcase", self.report())

    def test_changes_nothing_else_outside_the_content_region(self):
        self.run_script("--date", "2026-01-05", "--lang", "fr-CH", title="Quarterly review")
        template = new_report.TEMPLATE.read_bytes().decode("utf-8").split("\r\n")
        report = self.report().split("\r\n")
        head = template.index(new_report.START) + 1
        tail_t, tail_r = template.index(new_report.END), report.index(new_report.END)
        pairs = list(zip(template[:head], report[:head])) + list(zip(template[tail_t:], report[tail_r:]))
        self.assertEqual(len(template) - tail_t, len(report) - tail_r)
        changed = [new for old, new in pairs if old != new]
        self.assertEqual(len(changed), len(REWRITTEN), changed)
        for spot, line in zip(REWRITTEN, changed):
            self.assertIn(spot, line)

    def test_leaves_the_template_unchanged(self):
        before = hashlib.sha256(new_report.TEMPLATE.read_bytes()).hexdigest()
        self.run_script()
        self.assertEqual(hashlib.sha256(new_report.TEMPLATE.read_bytes()).hexdigest(), before)

    def test_sets_the_escaped_title_in_the_tab_the_top_bar_and_the_footer(self):
        self.run_script(title='Q3 & <review> "draft"')
        text = self.report()
        escaped = "Q3 &amp; &lt;review&gt; &quot;draft&quot;"
        self.assertIn(f"<title>{escaped}</title>", text)
        self.assertIn(f'title="Back to top">{escaped}</a>', text)
        self.assertIn(f'<span class="site-footer__title">{escaped}</span>', text)

    def test_collapses_whitespace_in_the_title(self):
        self.run_script(title="  Line one\n  line two\t")
        self.assertIn("<title>Line one line two</title>", self.report())

    def test_a_title_inside_the_content_is_left_alone(self):
        self.write("content.html", FRAGMENT.replace("<h2>", "<svg><title>Chart</title></svg>\n  <h2>"))
        self.run_script(title="Page")
        self.assertIn("<title>Page</title>", self.report())
        self.assertIn("<svg><title>Chart</title></svg>", self.content_region())

    def test_formats_the_footer_date(self):
        self.run_script("--date", "2026-01-05")
        self.assertIn('<time datetime="2026-01-05">5 January 2026</time>', self.report())

    def test_the_footer_date_defaults_to_today(self):
        days = {datetime.date.today()}
        self.run_script()
        days.add(datetime.date.today())
        stamps = [f'<time datetime="{d.isoformat()}">{new_report.display_date(d)}</time>' for d in days]
        self.assertTrue(any(s in self.report() for s in stamps), stamps)

    def test_sets_the_page_language(self):
        self.run_script("--lang", "fr-CH")
        self.assertIn('<html lang="fr-CH">', self.report())

    def test_keeps_the_template_crlf_newlines(self):
        self.run_script()
        raw = self.output.read_bytes()
        self.assertGreater(raw.count(b"\r\n"), 1000)
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))

    def test_an_lf_template_gives_an_lf_report(self):
        self.use_template(MINIMAL)
        self.write("content.html", FRAGMENT, newline="\r\n")
        self.assertEqual(self.run_script()[0], 0)
        self.assertNotIn(b"\r", self.output.read_bytes())

    def test_drops_the_fragment_bom(self):
        self.write("content.html", FRAGMENT, bom=True)
        self.run_script()
        self.assertNotIn("﻿", self.report())
        self.assertFalse(self.output.read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_force_overwrites_an_existing_report(self):
        self.output.write_text("old", encoding="utf-8")
        self.assertEqual(self.run_script("-f")[0], 0)
        self.assertIn("Sample report", self.report())


class RefusalTests(Workspace):
    def assertRefused(self, *extra, message, **kwargs):
        before = self.output.read_bytes() if self.output.is_file() else None
        code, out, err = self.run_script(*extra, **kwargs)
        self.assertEqual((code, out), (1, ""))
        self.assertIn(message, err)
        self.assertEqual(self.output.read_bytes() if self.output.is_file() else None, before)
        self.assertEqual([p.name for p in self.dir.iterdir() if p.suffix == ".tmp"], [])

    def test_an_empty_title(self):
        self.assertRefused(title=" \n ", message="the title is empty")

    def test_a_malformed_date(self):
        for date in ("2026-13-01", "2026-02-30", "30.10.2026", "2026-2-1", ""):
            with self.subTest(date=date):
                self.assertRefused("--date", date, message="invalid --date")

    def test_a_malformed_language(self):
        for lang in ("en_US", "e", "fr CH", "", "english-language-tag"):
            with self.subTest(lang=lang):
                self.assertRefused("--lang", lang, message="invalid --lang")

    def test_a_missing_fragment(self):
        self.assertRefused(content="nope.html", message="content fragment not found or not readable")

    def test_a_blank_fragment(self):
        self.write("content.html", "  \n\n\t\n")
        self.assertRefused(message="the content fragment is empty")

    def test_a_fragment_with_the_markers(self):
        self.write("content.html", f"{new_report.START}\n{FRAGMENT}")
        self.assertRefused(message="must not contain the REPORT:CONTENT: markers")

    def test_a_fragment_that_is_not_utf8(self):
        (self.dir / "content.html").write_bytes(b"<p>caf\xe9</p>")
        self.assertRefused(message="content fragment is not UTF-8")

    def test_an_existing_output_without_force(self):
        self.output.write_text("old", encoding="utf-8")
        self.assertRefused(message="already exists; use -f to overwrite it")

    def test_a_missing_output_directory(self):
        self.output = self.dir / "missing" / "report.html"
        self.assertRefused(message="the output directory does not exist")

    def test_an_output_that_is_a_directory(self):
        self.output = self.dir
        self.assertRefused(message="the output is a directory")

    def test_the_template_as_output(self):
        self.use_template(MINIMAL)
        self.output = new_report.TEMPLATE
        self.assertRefused("-f", message="the output is the template itself")

    def test_a_missing_template(self):
        with mock.patch.object(new_report, "TEMPLATE", self.dir / "gone.html"):
            self.assertRefused(message="template not found or not readable")

    def test_a_damaged_template(self):
        markers = "it needs exactly one"
        damages = {
            "no start marker": (MINIMAL.replace(new_report.START + "\n", ""), markers),
            "two end markers": (MINIMAL.replace("</main>", new_report.END + "\n</main>"), markers),
            "markers swapped": (MINIMAL.replace("START", "TMP").replace("END", "START").replace("TMP", "END"), markers),
            "no lang": (MINIMAL.replace(' lang="en"', ""), "0 <html lang> attributes"),
            "no title": (MINIMAL.replace("<title>Report Template</title>\n", ""), "0 <title> elements"),
            "no top bar title": (MINIMAL.replace('class="topbar__title"', 'class="topbar"'), "0 topbar__title"),
            "no footer title": (MINIMAL.replace("site-footer__title", "footer-title"), "0 site-footer__title"),
            "no footer date": (MINIMAL.replace(' datetime="2026-10-30"', ""), "0 site-footer <time>"),
        }
        for name, (text, message) in damages.items():
            with self.subTest(name):
                self.use_template(text)
                self.assertRefused(message=f"the template is damaged: {message}")


class WarningTests(Workspace):
    def warnings(self, fragment):
        self.write("content.html", fragment)
        code, _, err = self.run_script("-f")
        self.assertEqual(code, 0)
        return err

    def test_a_clean_fragment_warns_nothing(self):
        fragment = FRAGMENT.replace("</article>", '  <p><a href="https://example.com">A web link</a></p>\n'
                                                  '  <h2 id="risks">Risks</h2>\n</article>')
        self.assertEqual(self.warnings(fragment), "")

    def test_not_exactly_one_h1(self):
        self.assertIn("has 2 <h1> elements", self.warnings(FRAGMENT + "<h1>Again</h1>\n"))
        self.assertIn("has 0 <h1> elements", self.warnings(FRAGMENT.replace("h1", "p")))

    def test_external_resources(self):
        for extra in ('<img src="https://example.com/a.png" alt="">', "<div class=\"x\"></div><link rel=icon>",
                      '<svg><image href="x" srcset="http://example.com/b.png 2x"/></svg>'):
            with self.subTest(extra=extra):
                self.assertIn("loads external resources", self.warnings(FRAGMENT + extra))

    def test_scripts_and_styles(self):
        for extra in ("<script>alert(1)</script>", "<style>p{}</style>", '<p style="color:red">x</p>'):
            with self.subTest(extra=extra):
                self.assertIn("a style= attribute", self.warnings(FRAGMENT + extra))

    def test_escaped_markup_in_code_is_not_a_finding(self):
        self.assertEqual(self.warnings(FRAGMENT + "<pre><code>&lt;script&gt; &lt;h1&gt;</code></pre>\n"), "")

    def test_reserved_ids(self):
        err = self.warnings(FRAGMENT.replace("<h2>", '<h2 id="toc">').replace("<p ", '<p id="icon-star" '))
        self.assertIn("ids the template reserves: icon-star, toc", err)


class UsageTests(Workspace):
    def test_a_missing_option_is_a_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            new_report.main(["-c", "content.html", "-o", "report.html"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
