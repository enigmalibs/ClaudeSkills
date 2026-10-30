# FEATURE-9E0C-PHASE02 — Wire /review to html-report

## Summary

`/review`'s HTML report is now an `html-report` report, built from the PHASE01 fragment:
- `skills/review-standards/SKILL.md` (`2.0.0`) — *HTML rendering* now says:
  - fill `templates/report-content.html` into a scratchpad fragment;
  - build it with `html-report`'s `new_report.py`, giving the exact command (title, fragment, output, `-f` for same-day reruns, `--date`);
  - on a warning, fix the fragment and rebuild; never edit the output or read the template;
  - on a refusal or with no Python 3, the Markdown stays the only report.

  The 17-placeholder list is gone. `templates/report.html` is deleted.
- `commands/review.md` (`1.5.0`):
  - Phase 1 also loads `html-report`, for its build script only;
  - Phase 5 builds the HTML per the skill, or prints `review: HTML report skipped — <reason>.`;
  - *Rules* allow the scratchpad fragment and the build script.
- `README.md`:
  - Python's role for `/review`;
  - `/review` needs `review-standards` and `html-report`;
  - the `/review` section names `html-report`.

## Files/modules touched

- Modified: `skills/review-standards/SKILL.md`, `commands/review.md`, `README.md`
- Deleted: `skills/review-standards/templates/report.html`
- Modified: `docs/roadmap.md`, `docs/plan/FEATURE-9E0C.md` (statuses; the item is now `DONE`)
- Created: `docs/done/FEATURE-9E0C-PHASE02.md`

## Deviations & follow-ups

- **Existing reports:** HTML reports already written in other repositories keep the old look until `/review` runs again for that scope and date.
- **Size budget:** `SKILL.md` is 9,097 bytes. That is within its "≤ 9 KB" budget read as 9,216 bytes, but not if read as 9,000; it was 9,125 before this dev.
- **Prerequisite:** the HTML report now needs Python 3 and the `html-report` skill installed. The README's install loops already link every skill folder.

## Decisions taken at build time

| Question                                    | Chosen                                                                                                          | Why                                                                                                     |
|---------------------------------------------|-----------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| How `/review` finds the build script        | Load `html-report`; its printed base directory locates `scripts/new_report.py`                                  | Skill install paths vary (user or project scope); loading by name is how the house commands find skills |
| Which `html-report` steps `/review` follows | The build only. The fragment replaces gather, plan, write and the catalogue, and there is no headless verify    | `/review` never asks questions, and runs only read-only git, `dotnet` and this script                   |
| Skip-line wording                           | `review: HTML report skipped — <reason>.`                                                                       | Matches `/review`'s other `review: …` console lines                                                     |
| Where the fragment lives                    | The reviewer's scratchpad, like the findings file                                                               | `/review` writes nothing else to the repository                                                         |
| README *What to install* wording            | "`/review` needs `review-standards` and `html-report`", and "The *other* stack and tooling skills are optional" | `html-report` is a tooling skill that `/review` now requires                                            |

## Build/test evidence

Nothing to build. The run's baseline (34 + 51 tests OK) is recorded in `docs/done/FEATURE-9E0C-PHASE01.md`.

- **Stale references** — `grep` for `templates/report.html` and the old placeholder names in `commands/`, `skills/review-standards/` and the README: none. The only `{{…}}` left are the new fragment's own placeholders.
- **Frontmatter**:
  - `SKILL.md`: `name: review-standards`, version `2.0.0`, description unchanged (267 characters, no `: `);
  - `review.md`: version `1.5.0`, description unchanged.
- **Paths** — `templates/report-content.html` and `templates/report.md` exist; `templates/report.html` is gone.
- **Walk-through of `/review` Phase 5** on a sample, in a scratch repository that already holds `docs/review/2026-10-30-feature-3a7f.md`:
  - the command was copied from `SKILL.md`, then the placeholders and `py -3` were substituted;
  - it printed `wrote docs/review/2026-10-30-feature-3a7f.html` with no warning, exit 0;
  - the rerun overwrote the file, exit 0;
  - `<title>` is "Code review — feature-3a7f — 2026-10-30" and both `datetime` values are `2026-10-30`.
- **Fidelity, Markdown → HTML** (script):
  - the 6 finding ids appear in the same order;
  - all 12 locations are present;
  - all 20 *Why it matters*, *Recommended fix*, *Rule*, *Outside the plan* and *Done doc vs diff* sentences are present verbatim.
- **README** — 19 relative links resolve; every table is column-aligned.
- **Suites** — `py -3 -B -m unittest discover -s skills/html-report/scripts`: 34 tests OK; `… -s skills/dev-workflow/scripts`: 51 tests OK.
- **Documentation sweep** — the README edits above were this dev's planned steps. The README's `review-standards` row ("…checklists and templates for `/review`") and its `/review` table row ("writes two report files") are still accurate. There is no `CLAUDE.md`, `AGENTS.md`, `CHANGELOG.md` or `CONTRIBUTING.md`.
