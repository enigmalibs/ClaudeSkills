#!/usr/bin/env python3
"""Build an HTML report from the html-report skill's template and a content fragment.

  new_report.py -t TITLE -c FRAGMENT -o OUTPUT [-f] [--date YYYY-MM-DD] [--lang TAG]

Copies ../templates/report.html, sets the title (browser tab, top bar, footer), the footer date and the
page language, and replaces everything between the REPORT:CONTENT:START / END marker lines with the
fragment. The rest of the template — styles, script, icons, embedded fonts — is copied as it is.

Standard library only; runs on Linux, macOS and Windows.
Exit 0 = written (warnings go to stderr), 1 = refused (nothing written), 2 = usage error.
"""

import argparse
import datetime
import html
import os
import re
import sys
import tempfile
from pathlib import Path

PROG = "new_report.py"
TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "report.html"
START = "<!-- REPORT:CONTENT:START -->"
END = "<!-- REPORT:CONTENT:END -->"
MARKER = "REPORT:CONTENT:"
MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LANG_TAG = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{1,8})*$")

# The spots a build rewrites, each expected exactly once before (HEAD) or after (TAIL) the content region.
HTML_LANG = re.compile(r'(<html\b[^>]*\blang=")([^"]*)(")')
TITLE_ELEMENT = re.compile(r"(<title>)(.*?)(</title>)", re.S)
TOPBAR_TITLE = re.compile(r'(<a\b[^>]*\bclass="topbar__title"[^>]*>)(.*?)(</a>)', re.S)
FOOTER_TITLE = re.compile(r'(<span\b[^>]*\bclass="site-footer__title"[^>]*>)(.*?)(</span>)', re.S)
FOOTER_DATE = re.compile(r'(<footer\b[^>]*\bclass="site-footer"[^>]*>.*?<time\b[^>]*\bdatetime=")'
                         r'([^"]*)("[^>]*>)(.*?)(</time>)', re.S)
ID_ATTR = re.compile(r"""\bid\s*=\s*["']([^"']+)["']""", re.I)

# Content checks: a match is a warning, never a refusal.
H1 = re.compile(r"<h1[\s>]", re.I)
EXTERNAL = re.compile(r"""\b(?:src|srcset)\s*=\s*["']?\s*https?:|url\(\s*["']?\s*https?:|<link\b""", re.I)
SCRIPT_OR_STYLE = re.compile(r"""<script\b|<style\b|<[^>]*\sstyle\s*=""", re.I)


class Refused(Exception):
    """A build the script will not run. Nothing has been written."""


def display_date(day):
    return f"{day.day} {MONTHS[day.month - 1]} {day.year}"


def parse_date(text):
    if text is None:
        return datetime.date.today()
    try:
        if not ISO_DATE.match(text):
            raise ValueError
        return datetime.date.fromisoformat(text)
    except ValueError:
        raise Refused(f"invalid --date '{text}': expected a calendar date as YYYY-MM-DD") from None


def read_text(path, what):
    """The file's text, BOM dropped and newlines as \\n; and whether it had a BOM and CRLF newlines."""
    try:
        raw = Path(path).read_bytes()
    except OSError as error:
        raise Refused(f"{what} not found or not readable: {path} ({error.strerror})") from None
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise Refused(f"{what} is not UTF-8: {path}") from None
    crlf = "\r\n" in text
    return text.replace("\r\n", "\n").replace("\r", "\n"), raw.startswith(b"\xef\xbb\xbf"), crlf


def replace_once(pattern, text, part, what, build):
    """Rewrite the one match of PATTERN in TEXT with BUILD(match); refuse unless there is exactly one."""
    matches = len(pattern.findall(text))
    if matches != 1:
        raise Refused(f"the template is damaged: {matches} {what} in its {part} (expected 1): {TEMPLATE}")
    return pattern.sub(build, text)


def split_template(text):
    """The template's text up to its start marker line, and from its end marker line on."""
    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines) if START in line]
    ends = [i for i, line in enumerate(lines) if END in line]
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise Refused(f"the template is damaged: it needs exactly one '{START}' line, then one '{END}' line: "
                      f"{TEMPLATE}")
    return "\n".join(lines[:starts[0] + 1]), "\n".join(lines[ends[0]:])


def content_warnings(fragment, reserved):
    warnings = []
    h1 = len(H1.findall(fragment))
    if h1 != 1:
        warnings.append(f"the content has {h1} <h1> elements; a report has exactly one, the doc-title")
    if EXTERNAL.search(fragment):
        warnings.append("the content loads external resources (src, srcset or url() with http, or <link>); "
                        "embed them as inline SVG or data: URIs so the report renders offline")
    if SCRIPT_OR_STYLE.search(fragment):
        warnings.append("the content has a <script>, a <style> or a style= attribute; "
                        "the template provides all styling and behaviour")
    clashes = sorted({i for i in ID_ATTR.findall(fragment) if i in reserved or i.startswith("icon-")})
    if clashes:
        warnings.append(f"the content uses ids the template reserves: {', '.join(clashes)}")
    return warnings


def build(title, content, output, force=False, date=None, lang="en"):
    """Write the report; return the content warnings. Raises Refused before writing anything."""
    title = " ".join(title.split())
    if not title:
        raise Refused("the title is empty")
    if not LANG_TAG.match(lang):
        raise Refused(f"invalid --lang '{lang}': expected a language tag such as en, fr or de-CH")
    day = parse_date(date)

    fragment, _, _ = read_text(content, "content fragment")
    fragment = fragment.strip("\n")
    if not fragment.strip():
        raise Refused(f"the content fragment is empty: {content}")
    if MARKER in fragment:
        raise Refused(f"the content fragment must not contain the {MARKER} markers; "
                      f"pass only what goes between them: {content}")

    output = Path(output)
    if output.is_dir():
        raise Refused(f"the output is a directory: {output}")
    if not output.parent.is_dir():
        raise Refused(f"the output directory does not exist: {output.parent}")
    if output.exists():
        if TEMPLATE.exists() and os.path.samefile(output, TEMPLATE):
            raise Refused(f"the output is the template itself: {output}")
        if not force:
            raise Refused(f"{output} already exists; use -f to overwrite it")

    text, bom, crlf = read_text(TEMPLATE, "template")
    head, tail = split_template(text)
    escaped = html.escape(title)

    def retitle(m):
        return m.group(1) + escaped + m.group(3)

    def redate(m):
        return m.group(1) + day.isoformat() + m.group(3) + display_date(day) + m.group(5)

    head = replace_once(HTML_LANG, head, "head", "<html lang> attributes", lambda m: m.group(1) + lang + m.group(3))
    head = replace_once(TITLE_ELEMENT, head, "head", "<title> elements", retitle)
    head = replace_once(TOPBAR_TITLE, head, "head", "topbar__title links", retitle)
    tail = replace_once(FOOTER_TITLE, tail, "footer", "site-footer__title spans", retitle)
    tail = replace_once(FOOTER_DATE, tail, "footer", "site-footer <time> elements", redate)
    reserved = set(ID_ATTR.findall(head + "\n" + tail))

    report = f"{head}\n{fragment}\n{tail}"
    if crlf:
        report = report.replace("\n", "\r\n")
    data = (b"\xef\xbb\xbf" if bom else b"") + report.encode("utf-8")

    handle, temp = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
        os.replace(temp, output)
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise
    return content_warnings(fragment, reserved)


def parse_args(argv):
    parser = argparse.ArgumentParser(prog=PROG, description=__doc__.splitlines()[0])
    parser.add_argument("-t", "--title", required=True,
                        help="the report title, plain text: browser tab, top bar and footer")
    parser.add_argument("-c", "--content", required=True, metavar="FRAGMENT",
                        help="UTF-8 HTML fragment holding the doc-header and the article, nothing else")
    parser.add_argument("-o", "--output", required=True, help="the HTML file to write")
    parser.add_argument("-f", "--force", action="store_true", help="overwrite OUTPUT if it exists")
    parser.add_argument("--date", metavar="YYYY-MM-DD", help="the footer's 'Last updated' date (default: today)")
    parser.add_argument("--lang", default="en", metavar="TAG",
                        help="the page language, e.g. en, fr, de-CH (default: en)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        warnings = build(args.title, args.content, args.output, args.force, args.date, args.lang)
    except Refused as refusal:
        print(f"{PROG}: {refusal}", file=sys.stderr)
        return 1
    print(f"{PROG}: wrote {args.output}")
    for warning in warnings:
        print(f"{PROG}: warning: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
