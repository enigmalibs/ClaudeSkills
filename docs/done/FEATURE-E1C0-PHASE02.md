# FEATURE-E1C0-PHASE02 — Component catalogue

## Summary

Added `skills/html-report/reference/components.md` (322 lines). It is the markup reference for everything a report's content region can hold:
- the fragment shape (`doc-header` + `article.doc`, `data-numbered`, `data-toc-title`)
- headings, text, callouts, badges, figures (with the `fig-*` paint classes), tables and key figures
- quotes, code (automatic copy button, `data-no-copy`), expanders and expander groups
- lists and checklists, separators, `grid-2`
- what print does, and a *Do not* list that includes the template's reserved ids

Everything was derived from the template's stylesheet comments, script and showcase. Its class names differ from the Lodjx catalogue (`badge--accent`, `fig-accent`, `#icon-*`).

## Files/modules touched

- Created: `skills/html-report/reference/components.md`
- Modified: `docs/roadmap.md`, `docs/plan/FEATURE-E1C0.md` (statuses)
- Created: `docs/done/FEATURE-E1C0-PHASE02.md`

## Deviations & follow-ups

- None against the plan. The catalogue stays under the ~350-line target.
- The checker and the assembled fragment live in the session scratchpad, not the repository. Re-running them after a template update would need a copy; the obvious place is a test in `scripts/`, if the template starts changing often.

## Decisions taken at build time

| Question                              | Chosen                                                                | Why                                                                                                  |
|---------------------------------------|-----------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| Footer and `<title>` in the catalogue | Stated as set by the script; not part of the fragment                 | The template's "How to use" asks for them, and `new_report.py` does it — one source of truth         |
| Document `data-no-toc` side effects   | Yes: no number, no generated id, no `#` link                          | The script filters those headings out before numbering; a reader linking to one needs an explicit id |
| Expanders: when to use                | Detail only; key messages stay outside                                | Hidden content is easy to miss on screen even though it prints open                                  |
| A *Printing* section                  | Short paragraph: what print does, and that the fragment needs nothing | Authors otherwise add print-only markup or worry about closed expanders                              |
| Reserved ids                          | Listed in *Do not*, matching what `new_report.py` warns about         | The two stay consistent; the script derives its list from the template                               |

## Build/test evidence

Nothing to build. The baseline is the one recorded in `docs/done/FEATURE-E1C0-PHASE01.md`: 51 tests, OK, with no warnings.

- **Classes and icons** — a checker read the 15 `html` snippets and the backticked class names in prose and tables:
  - all 52 class names are defined in the template's stylesheet or set by its script;
  - all 4 `#icon-*` references are `<symbol>`s in the template;
  - result: no undefined class, no missing icon.
- **Every snippet in one fragment** — the checker nested all snippets in the article of the first one (165 lines, with a 1×1 PNG data URI standing in for `…`). `new_report.py` built it with no warning.
- **Render (headless Edge)**:
  - `--dump-dom`: 5 contents links, 5 heading numbers and 1 copy button (the `data-no-copy` block correctly has none);
  - full-page light-theme screenshot (`--blink-settings=preferredColorScheme=1`): every component renders, figures and the table are numbered, and the expander group shows one open item;
  - `--print-to-pdf`: 3 A4 pages.
- **Consistency** — nothing contradicts the template's "How to use" section: the title and footer steps are delegated to the script, and the content-region, `h1`, `data-numbered`, `data-no-toc` and `data-toc-title` rules match.
- **Tests** — `py -3 -B -m unittest discover -s skills/html-report/scripts` gives 34, OK; `… -s skills/dev-workflow/scripts` gives 51, OK.
- **Documentation sweep** — no user-facing doc is made wrong by this dev (the skill is still not wired up); nothing edited.
