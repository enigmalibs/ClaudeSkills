# FEATURE-E1C0-PHASE03 — SKILL.md and README entry

## Summary

This phase wires the skill up:
- `skills/html-report/SKILL.md` (version `1.0.0`) — frontmatter with a precise trigger description, then:
  - the rule never to read the template;
  - a file map;
  - the six-step workflow: gather, plan, write the fragment, build, verify, report. The build step has an options table and the refusal and warning behaviour; the verify step gives headless Edge/Chrome commands for the DOM, both themes and PDF;
  - how to revise an existing report by extracting its content region;
  - writing rules and the language policy.
- `README.md` — the skill counts (17, with 3 tooling), the Python prerequisite, a *Tooling* catalogue row and the second test command.

## Files/modules touched

- Created: `skills/html-report/SKILL.md`
- Modified: `README.md`
- Modified: `docs/roadmap.md`, `docs/plan/FEATURE-E1C0.md` (statuses; the item is now `DONE`)
- Created: `docs/done/FEATURE-E1C0-PHASE03.md`

## Deviations & follow-ups

- **Follow-up — trigger overlap:** the user-level `lodjx-html-report` skill (outside this repository) also triggers on "an HTML report". With both installed, Claude picks between them on description alone. The owner may want to narrow `lodjx-html-report` to Lodjx branding, or retire it in favour of `html-report`.
- **Follow-up — font and icon licences:** the template credits Plus Jakarta Sans and JetBrains Mono (OFL 1.1) and Lucide shapes (ISC) in a CSS comment, but the full licence texts are not bundled. Whether to add them is the owner's call.
- **Not verified:** the `sed` revise command needs a POSIX shell (Git Bash on Windows, which Claude Code uses). Pure PowerShell has no `sed`.

## Decisions taken at build time

| Question                                  | Chosen                                                      | Why                                                                                                          |
|-------------------------------------------|-------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| Where the working fragment lives          | A temporary directory; revising extracts it from the report | The report already holds its own source between the markers, so a second file to keep in sync is unnecessary |
| Default content language                  | The language of the request unless the user names another   | A French request expects a French report; the English interface labels are disclosed                         |
| How to verify the theme in a headless run | `--blink-settings=preferredColorScheme=1` / `=0`            | The template follows the OS preference; both values verified to switch it                                    |
| Python prerequisite wording in the README | Optional for the workflow, required by `html-report`        | Accurate for both; the workflow still runs without Python                                                    |
| Test command in the README                | Two lines, one per script                                   | `unittest discover -s` takes one start directory                                                             |

## Build/test evidence

Nothing to build. The baseline is the one in `docs/done/FEATURE-E1C0-PHASE01.md`.

- **Frontmatter** — `name: html-report` matches the folder; the description is 604 characters (limit 1,024); `metadata.version` is `"1.0.0"`; no `: ` or ` #` inside the plain-scalar description.
- **Paths** — all 4 paths SKILL.md names (`reference/components.md`, `scripts/new_report.py`, `scripts/test_new_report.py`, `templates/report.html`) exist.
- **README**:
  - every relative link resolves;
  - all 17 skill folders are listed, and nothing listed is absent;
  - every table is column-aligned (re-padded with `roadmap.py`'s `render_table`).
- **Walk-through of SKILL.md on a sample status report** (KPIs, table, badges, callout, list, expander, `[to confirm]` placeholders):
  - the build printed `wrote …` with no warning;
  - `--dump-dom` shows 4 contents links;
  - the dark-theme screenshot renders correctly;
  - the revise `sed` extract round-trips the fragment byte for byte.
- **Documented test commands**:
  - `py -3 -B -m unittest discover -s skills/html-report/scripts` — 34 tests, OK;
  - `… -s skills/dev-workflow/scripts` — 51 tests, OK.
- **Documentation sweep** — the README edits above are this dev's planned steps. There is no `CLAUDE.md`, `AGENTS.md`, `CHANGELOG.md` or `CONTRIBUTING.md`, and no command references the skill, so nothing else was stale.
