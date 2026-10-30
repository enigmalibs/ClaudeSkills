---
name: html-report
description: Use when producing a report or document as a single self-contained HTML file — a report, study, audit, technical note, proposal, status update or meeting summary built from the bundled report template (embedded fonts, light and dark themes, automatic table of contents and heading numbers, print and PDF ready, callouts, badges, numbered figures and tables, key-figure cards, expanders, code blocks with copy buttons). Triggers on "HTML report", "a report as an HTML file", "a self-contained HTML document", "the report template", or a request to turn notes, data or a draft into a shareable HTML report.
metadata:
  version: "1.0.0"
---

# HTML report

Builds a report as one self-contained HTML file from the bundled report template. You write only the **content region** — the document header and the article — and `scripts/new_report.py` splices it into a copy of the template. The template already carries the fonts, styles, both themes, the print layout, the table of contents and the copy buttons.

**Never open, read, edit or paste `templates/report.html`.** About 118 KB of it is base64 fonts. Everything you need about its markup is in `reference/components.md`, and the script is the only thing that touches the template.

Below, `<skill-dir>` is this skill's base directory.

## Files

| Path                         | Purpose                                                                                  |
|------------------------------|------------------------------------------------------------------------------------------|
| `reference/components.md`    | Markup and usage rules for every component — read it before writing any content          |
| `scripts/new_report.py`      | Builds a report: copies the template, sets title, date and language, splices the content |
| `scripts/test_new_report.py` | The script's tests (`python3 -B -m unittest discover -s <skill-dir>/scripts`)            |
| `templates/report.html`      | The report template — do not read it                                                     |

## Workflow

1. **Gather the content.** From the request and the material provided, establish:
   - the title, an optional subtitle and eyebrow (category);
   - the metadata (author, date, version, status…);
   - the sections and their key messages;
   - the data behind every table, chart and key figure.

   Ask for what is essential and missing. Never invent figures, names, dates or quotations. Leave a visible placeholder such as `[to confirm]` and list the placeholders when you report back.
2. **Plan the structure.** Lead with the conclusion: a `lead` paragraph and, when there are headline numbers, key-figure cards; then one `h2` per topic. Choose components by purpose:
   - a table for compared values;
   - a figure for a trend or a process;
   - a callout for the one point a reader must not miss;
   - badges for statuses;
   - an expander for detail not every reader needs.
3. **Write the content fragment.** Read `<skill-dir>/reference/components.md`, then write the fragment to a working file, e.g. `content.html` in a temporary directory. It holds the `<header class="doc-header">` followed by the `<article class="doc">`, and nothing else — no `<html>`, `<head>`, `<body>`, `<style>` or `<script>`. Save it as UTF-8.
4. **Build the report.**

   ```bash
   python3 "<skill-dir>/scripts/new_report.py" -t "Report title" -c content.html -o "Report title.html"
   ```

   On Windows, run `py -3` instead of `python3`.

   | Option            | Sets                                                                     |
   |-------------------|--------------------------------------------------------------------------|
   | `-t`, `--title`   | Plain text, escaped for you: the browser tab, the top bar and the footer |
   | `-c`, `--content` | The fragment file                                                        |
   | `-o`, `--output`  | The report to write; its directory must exist                            |
   | `-f`, `--force`   | Overwrite an existing output                                             |
   | `--date`          | The footer's *Last updated* date, `YYYY-MM-DD` (default: today)          |
   | `--lang`          | The page language, e.g. `fr`, `de-CH` (default: `en`)                    |

   It prints `wrote <path>` and exits 0, with one `warning:` line on stderr for each content-rule breach: not exactly one `h1`, external resources, scripts or styles, ids the template reserves. A refusal exits 1 and writes nothing: a missing or empty fragment, the content markers in the fragment, an existing output without `-f`, a bad date or language, or a damaged template.
5. **Verify.**
   - The script printed `wrote …` and no warning. To fix something, fix the fragment and re-run with `-f`; never edit the generated file.
   - If a Chromium browser is available (Edge, Chrome, Chromium), render the report headless with a `file:///` URL:
     - `--dump-dom` must contain `class="toc__link"` when the report has headings: the template's script ran.
     - Take a `--screenshot` (with `--window-size=1400,2000`) and look at it. `--blink-settings=preferredColorScheme=1` forces the light theme, `=0` the dark one.
     - `--print-to-pdf` checks the print layout.

     Otherwise ask the user to open the file and check the light theme, the dark theme and the print preview.
6. **Report** the output path, the outline (sections, figures, tables) and any placeholders left. Don't paste the HTML.

To **revise an existing report**:
1. Extract its content region into a fragment without reading the rest of the file, e.g. `sed -n '/REPORT:CONTENT:START/,/REPORT:CONTENT:END/{//!p}' report.html > content.html`.
2. Edit the fragment.
3. Rebuild with `-f`, passing the same title and `--date` unless they change.

## Writing rules

- One `h1`, the title. Sections start at `h2`, and `h2`–`h4` appear in the table of contents. Add `data-numbered` to the article for numbered headings.
- Figures and tables are numbered automatically. Captions hold only the description, with units and period.
- Keep the report self-contained: images as inline SVG or `data:` URIs, no linked fonts, images or scripts, no inline styles or colours.
- Keep paragraphs short, with one idea per section, and give the same badge tone to the same status throughout.
- Write dates in full, with a machine-readable `<time datetime>`.

## Language

The template's interface is English: *Contents*, *Figure*, *Table*, *Copy*, *Skip to content*, *Last updated* and the button tooltips. Write the content in the language of the request unless the user asks for another. For a report not in English:
- pass `--lang` (e.g. `--lang fr`);
- set `data-toc-title` on the article (e.g. `Sommaire`);
- tell the user that the interface labels stay English.
