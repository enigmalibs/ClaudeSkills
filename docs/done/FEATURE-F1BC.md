# FEATURE-F1BC — README documentation

## Summary

Replaced the one-line `README.md` stub with the repository's documentation (207 lines):
- what the repository contains, and its layout
- installation for user and project scope (bash and PowerShell; symlinks or copies), plus update and uninstall
- the plan-then-build workflow and the artifacts it writes in a project
- the five commands, as a table and one subsection each
- a catalogue of the 17 skills in three groups
- a short maintenance guide

## Files/modules touched

- Modified: `README.md`
- Modified: `docs/roadmap.md`, `docs/plan/FEATURE-F1BC.md` (status; skill count corrected)
- Created: `docs/done/FEATURE-F1BC.md`

## Deviations & follow-ups

- **Plan corrected:** the plan's context and acceptance criteria said 18 skills; the repository has 17. Corrected in the plan file. The README states 17, and the coverage check enumerates the `skills/` folders rather than trusting either number.
- **Not executed:** the PowerShell install snippet — `pwsh` is not installed on the build machine. It uses only `New-Item -ItemType Directory|SymbolicLink -Force` and `Get-ChildItem`. Worth one manual run on Windows.
- **Follow-up — license:** the repository has no `LICENSE` file, so the README claims none. Adding one (and a *License* section) is the owner's decision.
- **Line endings (recommendation only):** every file under `commands/` and `skills/` is CRLF, while `README.md` and the new `docs/` files are LF. A `.gitattributes` rule (e.g. `*.md text eol=lf`, or `eol=crlf` to match the existing files) would make this consistent.

## Decisions taken at build time

| Question                                | Chosen                                                                  | Why                                                                                               |
|-----------------------------------------|-------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| How to keep the README's tables aligned | Re-pad them with `roadmap.py`'s own `render_table`                      | Same character-count padding rule as the roadmap, and deterministic instead of hand-counted       |
| Link tool for the user-scope install    | `ln -sfn`, with the README warning that it replaces same-name entries   | Re-running the loop must pick up new skills without failing on existing links                     |
| Uninstall command                       | `find … -maxdepth 1 -type l -lname "<clone>/*" -delete`                 | Removes only links into the clone; the user's own commands and skills survive (verified)          |
| Skill versions in the catalogue         | Not listed (planned); the maintenance section explains the version line | Several skills carry no version line, and the others change often                                 |
| Document `docs/` in the layout tree     | Yes, as "this repository's own roadmap, plans and completion records"   | This dev created it; a reader would otherwise wonder why a skills repository has a `docs/` folder |

## Build/test evidence

Nothing to build: this dev is documentation only. Verification:

- **Tables, links, coverage** — a checker script, run on the written file, reported every table column-aligned, every relative link resolving, and all 5 commands and 17 skills documented, with no catalogue entry naming a missing skill. The checker lives outside the repository; it reuses `roadmap.split_row` / `render_table`.
- **Install, update, uninstall (bash)** — run against a throwaway `HOME` with a local clone:
  - install linked 5 commands and 17 skills, and the links resolve
  - a re-run left 5 + 17 links and no nested links
  - uninstall removed every link and kept an unrelated skill folder
- **Documented test command** — `python3 -B -m unittest discover -s skills/dev-workflow/scripts`: 46 tests, OK.
- **Roadmap** — `roadmap.py fmt --check`: already formatted.
- **Documentation sweep** — the dev's only user-facing change is `README.md` itself. There is no `CLAUDE.md`, `AGENTS.md`, `CHANGELOG.md` or `CONTRIBUTING.md`, so nothing was stale.
