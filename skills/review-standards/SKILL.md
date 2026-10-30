---
name: review-standards
description: Use when running the house /review code review — the severity scale, the review dimensions and their rulebook, the finding and report shapes, and the reference checklists for SOLID, XAML, logging, exceptions, security, style, performance and tests. Loaded by /review.
metadata:
  version: "2.0.0"
---

# Review standards — the house code-review checklist

What `/review` measures code against and how it writes what it found. The house convention skills are the rulebook; this skill adds the severity scale, the dimensions, the shapes `/interview` and `/vibe` consume, and checklists only for what no house skill states.

## Severities

| Severity | Meaning | Examples |
|---|---|---|
| Critical | Data loss, security exposure, crash or deadlock in normal use | path traversal on a user path, `.Result` on the UI thread, a swallowed exception on a save path |
| High | A bug with user-visible impact, or a design breach that is expensive to change later | captive dependency, service locator, logic in code-behind, `catch` swallowing an I/O failure |
| Medium | A house-convention breach that hurts maintainability but not behaviour | interpolated log messages, a repeated setter group that should be a `Style`, a 6-dependency constructor |
| Low | Style, naming, minor redundancy | an unused `xmlns`, a `TODO` without owner, a commented-out block |

A finding's severity is the worst plausible consequence of the pattern, not of its most benign location. A house convention an existing codebase diverges from *consistently* is one Low finding per convention ("divergence"), never one per location.

## Dimensions

Reviewed in this order. *Rulebook* names the house skill whose rules apply as written — never restated here; *Reference* is this skill's checklist for what the rulebook does not cover.

| Key | Checks | Rulebook | Reference | Applies when |
|---|---|---|---|---|
| `SOLID` | responsibilities, extension points, substitutability, interfaces, dependencies and lifetimes | dotnet-di-design, csharp-extension-methods | `reference/solid.md` | always |
| `XAML` | redundancy, resources, code-behind, bindings, layout | avalonia or wpf; enigma-avalonia-desktop and enigma-icons-avalonia when referenced | `reference/xaml.md` | `.axaml`/`.xaml` present |
| `LOG` | logger acquisition, templates, levels, exceptions, hot paths, sensitive data | — | `reference/logging.md` | always |
| `EXC` | catch blocks, throwing, disposal, async failures, UI handlers, global handlers | dotnet-async | `reference/exceptions.md` | always |
| `ASYNC` | `Task` APIs, cancellation, blocking, UI-thread marshaling | dotnet-async | — | always |
| `MVVM` | ViewModels, properties, commands, view wiring | communitytoolkit-mvvm; avalonia or wpf | — | CommunityToolkit.Mvvm referenced |
| `TEST` | tests of the reviewed behaviour | xunit-v3 | `reference/tests.md` | always — no test project is itself a finding |
| `SEC` | secrets, paths, injection, deserialisation, transport, data at rest | — | `reference/security.md` | always |
| `STYLE` | naming, suppressions, dead code, usings, file size | dotnet-solution-config, dotnet-solution-setup | `reference/style.md` | always |
| `PERF` | blocking, allocations, collections, I/O, startup and UI | dotnet-async | `reference/performance.md` | always |

A rulebook-only dimension (`ASYNC`, `MVVM`) is checked against the skill's rules and its *Common mistakes* table: each row is a check, its fix column the recommended fix.

## Finding shape

This is what `/interview` and `/vibe` read to plan a `CODE-REVIEW` item (one phase per finding, severity-ordered), so every field is mandatory:

```markdown
### EXC-03 — [High] Empty catch blocks swallow I/O errors on the save path

**Locations**
- `src/App/Services/FileSync.cs:88`
- `src/App/Services/FileSync.cs:142`
- `src/App/ViewModels/ExportViewModel.cs:61`

**Why it matters** — a failed write is reported as success; the user loses data without a message.

**Recommended fix** — catch `IOException` only, log it with the exception as first argument and surface it through `InfoBar`; let everything else propagate.

**Rule** — review-standards `reference/exceptions.md` §Catch blocks; dotnet-async *CancellationToken*.
```

- `<KEY>-NN`: the dimension key and a two-digit counter per dimension, in order of discovery. Conformance findings are `PLAN-NN`.
- **One finding per pattern, never per location**: the same smell in 14 places is one finding with 14 locations and one fix. No cap on findings or locations.
- Every location is `path:line` from the repo root, one per line; a range is `path:line-line`.
- *Why it matters* states the consequence, not the rule. *Recommended fix* is one concrete change that closes every location. *Rule* cites the house skill section or the reference file section.
- Not a finding: generated code (`*.g.cs`, `obj/`), third-party code, line endings, a consistently applied divergence (see *Severities*), anything the baseline already reports as a build error.

## Plan conformance (work-item scope)

One block per reviewed work item, between the baseline and the findings:

```markdown
### FEATURE-3A7F — User authentication

| Criterion | Status | Evidence |
|---|---|---|
| 1. Login succeeds with valid credentials | met | `src/Auth/LoginService.cs:40`, `tests/Auth/LoginServiceTests.cs:18` |
| 2. Five failures lock the account for 15 minutes | partial | lockout exists (`LoginService.cs:72`) but lasts 5 minutes |
| 3. Audit entry per attempt | not met | no write to `IAuditLog` in the diff |

**Outside the plan** — `src/Auth/PasswordPolicy.cs` added without a criterion.
**Done doc vs diff** — `docs/done/FEATURE-3A7F.md` claims "unit tests for lockout"; none in the diff.
```

Status is `met`, `partial`, `not met` or `not verifiable` (a manual test, an external system). Every `partial`, `not met`, unplanned addition and unbacked claim is also a `PLAN-NN` finding, severity by consequence: an unmet security criterion is Critical, an unbacked done-doc claim Medium.

## Report structure

`docs/review/<yyyy-mm-dd>-<scope>.md` in the reviewed repo — `<scope>` is `solution`, the IDs lowercased joined by `-`, or the path's last segment; a same-day rerun overwrites. Its headings, in this order, from `templates/report.md`:

1. `# Code review — <scope> — <date>`
2. `## Scope & method` — solution, commits or files reviewed, dimensions, rulebook skills with their `metadata.version` (read from each skill's `SKILL.md` frontmatter on disk — its base directory is printed when it loads), inline or sub-agents.
3. `## Baseline` — `dotnet build` (errors; warnings by analyzer ID) and `dotnet test` (passed / failed / skipped), or why each did not complete.
4. `## Summary` — a tally table by severity and a three-line verdict.
5. `## Plan conformance` — work-item scope only.
6. `## Findings` — severity order, Critical first; within a severity, dimension order.
7. `## In good shape` — three to six lines: what the next dev should keep doing.
8. `## Hand-off` — the `/interview` and `/vibe` lines, verbatim from the template.

## HTML rendering

`docs/review/<yyyy-mm-dd>-<scope>.html`, an `html-report` report written after the Markdown and from it only: same sections, findings, order and text — the Markdown is the source of truth. Fill `templates/report-content.html` per its leading comment into a fragment in your scratchpad, then build it with `html-report`'s script (`py -3` on Windows):

```bash
python3 "<html-report dir>/scripts/new_report.py" -t "Code review — <scope> — <yyyy-mm-dd>" -c <fragment> -o docs/review/<yyyy-mm-dd>-<scope>.html -f --date <yyyy-mm-dd>
```

It prints `wrote <path>`. On a `warning:` line, fix the fragment and rebuild; never edit the output or read the template. A refusal, or no Python 3, leaves the Markdown as the only report: say why in one line.

## Budgets and reference files

`SKILL.md` ≤ 9 KB; each reference ≤ 6 KB. Read a reference only when its dimension is reviewed:

- [`reference/solid.md`](reference/solid.md) — the five principles as C# smells, and when not to flag.
- [`reference/xaml.md`](reference/xaml.md) — redundancy, resources, code-behind, bindings, layout, Avalonia vs WPF.
- [`reference/logging.md`](reference/logging.md) — logger acquisition, templates, levels, exceptions, hot paths, sensitive data.
- [`reference/exceptions.md`](reference/exceptions.md) — catch blocks, throwing, disposal, async, UI and global handlers.
- [`reference/security.md`](reference/security.md) — secrets, paths, injection, deserialisation, transport, data at rest.
- [`reference/style.md`](reference/style.md) — naming, suppressions, dead code, usings, formatting.
- [`reference/performance.md`](reference/performance.md) — blocking, allocations, collections, I/O, startup and UI.
- [`reference/tests.md`](reference/tests.md) — presence, assertions, isolation, coupling, test code quality.
