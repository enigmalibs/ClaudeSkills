# FEATURE-E1C0-PHASE01 — Template and build script

## Summary

The `html-report` skill gets its two working parts:
- `templates/report.html` — the supplied report template, copied byte for byte (SHA-256 `baf0d0e9a36ee9998a8140517b764e232ee16819f5c0ab3f048e955907386636`).
- `scripts/new_report.py` — builds a report from a content fragment:
  - copies the template;
  - sets the title (escaped) in the tab, the top bar and the footer, the footer date (`--date`, default today) and `<html lang>` (`--lang`, default `en`);
  - replaces the content region between the `REPORT:CONTENT` marker lines.

Structural problems refuse with exit 1 and write nothing: a damaged template, a bad fragment, a bad date or language, an existing output without `-f`. Content-rule breaches only warn: the `h1` count, external resources, scripts or styles, reserved ids.

## Files/modules touched

- Created: `skills/html-report/templates/report.html`
- Created: `skills/html-report/scripts/new_report.py`, `skills/html-report/scripts/test_new_report.py`
- Modified: `docs/roadmap.md`, `docs/plan/FEATURE-E1C0.md` (statuses; test count corrected)
- Created: `docs/done/FEATURE-E1C0-PHASE01.md`

## Deviations & follow-ups

- **Plan corrected:** the plan said the `roadmap.py` suite has 46 tests (a figure carried over from FEATURE-F1BC). It has 51, all passing at baseline. Corrected in the plan.
- **Not yet a skill:** the folder has no `SKILL.md` until PHASE03, so nothing loads it yet, and the README is not stale for now.
- **Line endings (recommendation only):** the template is CRLF in the working tree. With `core.autocrlf=true`, git stores it as LF, so a checkout on Linux/macOS gets an LF template. The script keeps whatever newline style the template has, and a test covers both.

## Decisions taken at build time

| Question                                    | Chosen                                                                               | Why                                                                                     |
|---------------------------------------------|--------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| Where the title/date/lang edits are applied | Only to the template text before and after the content region                        | A fragment's own `<title>` (SVG) or `<time>` must never be rewritten (tested)           |
| How "exactly once" is enforced              | Each rewritten spot must match exactly once, else the template is refused as damaged | A template update that moves or duplicates a spot fails loudly instead of half-applying |
| Reserved ids                                | Every id the template defines outside the content region, plus `icon-*`              | Follows the template if it changes; no hard-coded list                                  |
| Fragment newlines and BOM                   | BOM dropped; newlines converted to the template's style                              | PowerShell's `Out-File` writes a BOM; avoids mixed endings in one file                  |
| Atomic write                                | `mkstemp` in the output directory, then `os.replace`                                 | A failure never leaves a half-written report; no `.tmp` left behind (tested)            |
| Test isolation from the bundled template    | `mock.patch.object(new_report, "TEMPLATE", …)` for synthetic templates               | Damaged and LF templates are tested without touching the real one                       |

## Build/test evidence

Run baseline, taken on `feature/2026-10-30-html-report-skill` before this dev: there is no build step; `py -3 -B -m unittest discover -s skills/dev-workflow/scripts` gave 51 tests, OK, with no warnings and no failures.

After this dev:
- `py -3 -B -m unittest discover -s skills/html-report/scripts` — **34 tests, OK** (build, refusal, warning and usage cases).
- `py -3 -B -m unittest discover -s skills/dev-workflow/scripts` — **51 tests, OK**.
- `sha256sum skills/html-report/templates/report.html` matches `C:\Temp\template.html`, and the template is unchanged after a build (tested).
- Sample fragment built with `--date 2026-10-30`: `wrote …`, no warning.
  - Headless Edge `--dump-dom`: 3 table-of-contents links, 3 heading numbers, 1 copy button. The template's script ran.
  - Screenshot: title in the top bar and footer, the contents sidebar, numbered headings, the code block, *Last updated 30 October 2026*.
- `test_changes_nothing_else_outside_the_content_region` checks the "differs only in title, date, lang and content" criterion line by line.
- No `__pycache__` under `skills/`.
- Documentation sweep: no user-facing doc is made wrong by this dev (the skill is not wired up yet); nothing edited.
