**Status:** DONE
**Type:** FEATURE (multi-phase)
**Branches:** feature/feature-e1c0-phase01-template-script · feature/feature-e1c0-phase02-component-catalogue · feature/feature-e1c0-phase03-skill-readme
**Run:** feature/2026-10-30-html-report-skill

# FEATURE-E1C0 — html-report skill

## Objective

Add a skill `html-report` that turns a request — notes, data, a draft — into a single self-contained HTML report built from the report template supplied as `C:\Temp\template.html`. The template is bundled in the skill unchanged; Claude writes only the content region and a script splices it into a copy.

## Context & constraints

- A skill here is `skills/<name>/SKILL.md` (frontmatter `name` = folder, `description`, `metadata.version` semver) plus optional `reference/`, `templates/`, `scripts/` (README *Maintaining this repository*). `review-standards/templates/report.html` is the precedent for a bundled HTML template.
- The only script in the repo is `skills/dev-workflow/scripts/roadmap.py` — Python 3 stdlib, `py -3` on Windows, a `unittest` suite beside it (`test_roadmap.py`), refusals exit 1 with nothing written.
- The template (`<meta name="generator" content="Report template 1.0">`): 200,608 bytes, UTF-8 without BOM, CRLF, SHA-256 `baf0d0e9a36ee9998a8140517b764e232ee16819f5c0ab3f048e955907386636`. About 118 KB are three base64 `@font-face` lines (Plus Jakarta Sans roman/italic, JetBrains Mono — OFL 1.1; icons after Lucide — ISC). No external resource.
- Its "How to use" section defines the contract: replace everything between `<!-- REPORT:CONTENT:START -->` and `<!-- REPORT:CONTENT:END -->` with a `header.doc-header` and an `article.doc`; set the title in `<title>`, `.topbar__title` and `.site-footer__title`, and the date in the footer's `<time>`. Everything else — styles, script, fonts, icons — stays untouched.
- Ids outside the content region are the template's (`top`, `content`, `toc`, `toc-title`, `toc-toggle`, `numbering-toggle`, `theme-toggle`, `print-button`, `report-styles`, `report-fonts`, `icon-*`).
- A user-level skill `lodjx-html-report` (not in this repo) does the same for a different, branded template; it is prior art only.
- `core.autocrlf=true` in this clone; line endings are never normalized.

## Decisions

See *Decisions taken autonomously* below. In short: `templates/report.html` is a verbatim copy; `scripts/new_report.py` (Python stdlib) builds a report from a fragment; `reference/components.md` documents the markup; `SKILL.md` drives the workflow; the README lists the skill under *Tooling*.

## PHASE01 — Template and build script

**Status:** DONE

### Steps

1. Copy `C:\Temp\template.html` byte for byte to `skills/html-report/templates/report.html`.
2. Write `skills/html-report/scripts/new_report.py` (stdlib only, module docstring as usage, `main(argv=None)` returning the exit code, like `roadmap.py`):
   - `new_report.py -t TITLE -c FRAGMENT -o OUTPUT [-f] [--date YYYY-MM-DD] [--lang TAG]`; the template is `../templates/report.html` relative to the script (module constant, patchable in tests).
   - Title: whitespace and newlines collapsed to single spaces, must not be empty, HTML-escaped (`& < > "`); written into `<title>`, `.topbar__title` and `.site-footer__title`.
   - `--date` (default: today) sets the footer's `<time datetime>` and its text as `30 October 2026` (English month names, no locale dependence); a malformed date is refused.
   - `--lang` (default `en`) sets `<html lang>`; anything not shaped like a BCP 47 tag is refused.
   - Fragment: read as UTF-8 with any BOM dropped; refused when missing, unreadable, not UTF-8, blank, or containing a `REPORT:CONTENT:` marker. It replaces everything between the marker lines; the markers stay.
   - Template checks: exactly one start and one end marker line, in order; `<title>`, `.topbar__title`, `.site-footer__title` and the footer `<time>` present; otherwise a refusal naming what is missing.
   - Output: refused when its directory is missing, when it exists without `-f`, or when it is the template itself. Written through a temp file in the same directory, then replaced; the template's newline style is kept and applied to the fragment.
   - Warnings (stderr, exit 0): not exactly one `<h1`; external resources (`src`/`srcset` or `url(` with `http(s):`, `<link`); `<script`, `<style` or `style=` in the fragment; an `id` that collides with an id the template defines outside the content region, or starts with `icon-`.
   - Messages: `new_report.py: wrote <path>`; `new_report.py: <reason>` (exit 1, nothing written); `new_report.py: warning: <issue>`; argparse usage errors exit 2.
3. Write `skills/html-report/scripts/test_new_report.py` (`unittest`, the style of `test_roadmap.py`, no `__pycache__`) covering every rule above against the bundled template, plus minimal synthetic templates for the damaged-template and LF cases.

### Acceptance criteria

- `templates/report.html` hashes to the SHA-256 above.
- `py -3 -B -m unittest discover -s skills/html-report/scripts` passes; the `roadmap.py` suite still passes (51 tests).
- A build of a small sample fragment produces a file that differs from the template only in the title (3 places), the footer date, `lang` and the content region, and leaves the template unchanged.
- Rendered in headless Edge, the sample shows its title and content, and `--dump-dom` shows the generated table of contents.
- No `__pycache__` or build output is committed.

## PHASE02 — Component catalogue

**Status:** DONE

### Steps

1. Write `skills/html-report/reference/components.md`: markup and usage rules for everything the content region may hold, derived from the template's stylesheet comments, script and showcase — never from the Lodjx catalogue's class names. Sections:
   - the content fragment (`header.doc-header` with eyebrow, `h1.doc-title`, subtitle, `dl.doc-meta`; `article.doc` with `data-numbered` and `data-toc-title`);
   - headings (`h2`–`h5`, `data-no-toc`, generated and explicit ids, badges in headings);
   - text (`lead`, inline elements, `kbd`);
   - callouts (four tones, `#icon-*` icons, info by default);
   - badges (`badge--info|success|warning|error|accent`, `badge--dot`, one tone per status);
   - figures (embedded images, inline SVG rules, the `fig-*` paint classes);
   - tables (`table-wrap`, first-child `caption`, `scope`, `num`, `tfoot`);
   - key figures (`kpis`, `kpi__delta--up|down`);
   - quotes, code (escaping, automatic copy button, `data-no-copy`);
   - expanders (`details.expander`, `expander__body`, `open`, `expander-group` with a shared `name`, printed open, opened by links);
   - lists and checklists, separators, `grid-2`;
   - a *Do not* list (styles, scripts, colours, linked resources, a second `h1`, manual numbering, reserved ids).
2. Keep it to about 350 lines; every snippet copyable as is.

### Acceptance criteria

- Every class name used in the catalogue's snippets is defined in the template's stylesheet or set by its script, and every `#icon-*` it references is a `<symbol>` in the template (checked by script).
- All the catalogue's snippets, assembled into one fragment and built with `new_report.py`, produce no warning; the headless render shows each component.
- Nothing in the catalogue contradicts the template's own "How to use" section.

## PHASE03 — SKILL.md and README entry

**Status:** DONE

### Steps

1. Write `skills/html-report/SKILL.md`: frontmatter `name: html-report`, a precise trigger `description`, `metadata.version: "1.0.0"`; then
   - what the skill does, and the rule never to open or read `templates/report.html` (fonts) — `reference/components.md` is the markup reference and the script the only thing that touches the template;
   - a *Files* table;
   - the workflow: gather content (never invent figures, names, dates or quotes — leave `[to confirm]` placeholders and list them); plan the structure (conclusion first, components by purpose); write the fragment; build (`py -3` on Windows, `python3` elsewhere); verify (script output, headless render and `--dump-dom` when a browser is available, else ask the user to check both themes and the print preview); report the path, outline and placeholders;
   - writing rules and the language policy (content in the requested language with `--lang` and `data-toc-title`; the template's own labels stay English, and the user is told).
2. Update `README.md`: skill counts in *What's inside* (17 skills, 3 tooling), a row in the *Tooling* table, the Python prerequisite (also the `html-report` build script) and the test command in *Maintaining this repository*; tables kept aligned.

### Acceptance criteria

- The frontmatter parses, `name` equals the folder name, and the description is under 1,024 characters.
- Every path `SKILL.md` names exists in the skill folder.
- Following `SKILL.md` on a sample request produces a report with no warning, rendered in headless Edge.
- The README lists all 17 skills, every relative link resolves, every table is column-aligned, and both documented test commands pass.

## Out of scope

- Changing the template, localizing its interface labels (*Contents*, *Figure*, *Table*, *Copy*, button titles), or adding a logo or branding.
- The user-level `lodjx-html-report` skill.
- `LICENSE` files, including the full OFL / ISC texts for the template's embedded fonts and icons.
- PDF generation inside the script, a PowerShell or bash variant of it, CI.
- Line-ending normalization.

## Decisions taken autonomously

| Question                        | Chosen                                                                                                            | Why                                                                                                                                              | Alternatives rejected                                                    |
|---------------------------------|-------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| Where the template lives        | `templates/report.html`, a verbatim copy                                                                          | House layout (`reference/`, `templates/`, `scripts/`) and the `review-standards/templates/report.html` precedent; "asset" read as "bundled file" | `assets/template.html` (a fourth folder kind the README does not list)   |
| How a report is assembled       | A script splices a content fragment into a copy                                                                   | Claude never reads or rewrites ~118 KB of base64 fonts; the template cannot be corrupted                                                         | Claude copies and edits the file; a templating engine                    |
| Script language                 | Python 3 stdlib + `unittest`                                                                                      | Same as `roadmap.py`; runs on Windows (`py -3`); testable                                                                                        | bash (prior art, untestable here, needs Git Bash on Windows); PowerShell |
| What the script sets            | Title (3 places, escaped), footer date (`--date`, default today), `<html lang>` (`--lang`, default `en`)          | Exactly the template's "How to use" steps, plus the page language for screen readers                                                             | Title only; full localization of the template labels                     |
| Adapt the template              | No — byte-identical, hash recorded                                                                                | The showcase content is replaced on every build and doubles as the visual reference                                                              | Strip the showcase; rebrand                                              |
| Component documentation         | `reference/components.md`, loaded when writing content                                                            | Keeps `SKILL.md` short; one place for markup rules                                                                                               | Everything in `SKILL.md`; pointing Claude at the template's showcase     |
| Errors vs warnings              | Structural problems refuse (nothing written); content-rule breaches warn                                          | A broken structure breaks the page; rule breaches are author judgement                                                                           | Refuse everything; warn on everything                                    |
| Reserved ids                    | Derived from the template at run time                                                                             | Survives a future template update without a code change                                                                                          | A hard-coded list                                                        |
| Language policy                 | Content in the requested language; `--lang` + `data-toc-title`; template labels stay English and the user is told | Localizing CSS/JS strings means editing the template                                                                                             | English only; patching labels at build time                              |
| Verification                    | Script warnings, then headless Edge/Chrome render and `--dump-dom` when available                                 | Catches what a regex cannot (layout, generated TOC) without new tooling                                                                          | Script checks only; a browser-automation dependency                      |
| README placement                | *Tooling* group                                                                                                   | Like `dotnet-release` and `git-repo-hygiene`: a task tool, not a code convention                                                                 | A new *Documents* group for one skill                                    |
| Relation to `lodjx-html-report` | Independent; untouched; trigger overlap recorded as a follow-up                                                   | It lives outside the repo; merging or retiring it is the owner's call                                                                            | Replace or rename it                                                     |
| Version                         | `1.0.0`                                                                                                           | New skill, semver per the README                                                                                                                 | `0.1.0`                                                                  |
| Phasing                         | 3 phases: script, catalogue, skill + README                                                                       | One reviewable commit each; the skill is wired up last, once its parts exist                                                                     | One dev; script and catalogue together                                   |
