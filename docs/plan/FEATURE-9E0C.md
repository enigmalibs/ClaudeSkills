**Status:** DONE
**Type:** FEATURE (multi-phase)
**Branches:** feature/feature-9e0c-phase01-review-fragment · feature/feature-9e0c-phase02-review-wiring
**Run:** feature/2026-10-30-review-html-report

# FEATURE-9E0C — Review report on html-report template

## Objective

`/review` renders its HTML report with the `html-report` template instead of the bespoke page in `review-standards/templates/report.html`. `review-standards` keeps owning the review's shapes and supplies a review-shaped content fragment; `html-report` keeps owning the template and its build script, `scripts/new_report.py`.

## Context & constraints

- `review-standards` 1.2.0 *HTML rendering*: `docs/review/<date>-<scope>.html` is written after the Markdown report and from it only — same findings, same order, same text. Its `templates/report.html` is a 214-line page with 17 `{{placeholders}}`, its own CSS, a CSS-only severity filter (`:has` on checkboxes) and one `<details class="finding">` per finding, `open` for Critical and High.
- `/review` 1.4.0 (`commands/review.md`) Phase 5 step 2 writes that page; its rules allow only read-only git, `dotnet build` and `dotnet test`, and only the two report files as writes (it already keeps a scratchpad findings file).
- `html-report` 1.0.0: `new_report.py -t TITLE -c FRAGMENT -o OUTPUT [-f] [--date] [--lang]` splices a fragment (`header.doc-header` + `article.doc`) into a copy of the template. It warns on more than one `h1`, external resources, `<script>`/`<style>` and reserved ids; it refuses, writing nothing, on structural problems. `reference/components.md` is the markup catalogue: callouts, badges (`--info/--success/--warning/--error/--accent`, plain = neutral, `--dot`), tables (`div.table-wrap`, `caption` first, numbered only with a caption), key-figure cards (2–4), code blocks with copy buttons, expanders and `expander-group` (independent without `name`). `h2`–`h4` feed the contents. Claude never reads `templates/report.html`.
- `review-standards/SKILL.md` is 9,125 bytes; its budget is 9 KB, so the rewritten section must not grow it. References ≤ 6 KB each.
- Versions are semver in the frontmatter, bumped with every change (README *Maintaining this repository*).
- The README names `/review`'s skill dependencies (*What to install*) and Python's role (*Prerequisites*).
- `core.autocrlf=true`; line endings are never normalized.

## Decisions

See *Decisions taken autonomously*. In short: the template stays only in `html-report`; `review-standards/templates/report-content.html` replaces `templates/report.html` as a fragment skeleton; `/review` loads `html-report` and builds with its script; findings become expanders grouped under one `h3` per severity.

## PHASE01 — Review content fragment

**Status:** DONE

### Steps

1. Add `skills/review-standards/templates/report-content.html`, a content fragment for `html-report`, mirroring `templates/report.md` section for section:
   - A leading comment — the fill rules, dropped from the written fragment: values from the Markdown report only, HTML-escaped (`&`, `<`, `>` — C# generics included), `` `code` `` → `<code>`, `**bold**` → `<strong>`; repeat the blocks marked *one per …*; drop *Plan conformance* when the Markdown has none and a severity heading with no finding; the tone tables below; every comment dropped.
   - `header.doc-header`: eyebrow *Code review*; `h1.doc-title` = the Markdown title; subtitle = the Markdown's "Written by …" line; `dl.doc-meta` with Scope, Revision (`<branch> @ <sha>`), Date (`<time datetime>`), Findings (total).
   - `article.doc`, no `data-numbered`, one `h2` per Markdown section in its order: *Scope & method* (`ul`); *Baseline* (captioned table, `th scope="row"` steps, then the note); *Summary* (four key-figure cards Critical/High/Medium/Low, the captioned tally table with a severity badge per row, `num` cells and a `tfoot` total, then the three verdict lines); *Plan conformance* (one `h3` per item, a captioned criteria table with status badges, *Outside the plan*, *Done doc vs diff*); *Findings* (one `h3` per severity present, then an `expander-group` of `details.expander` with `id="<KEY-NN>"`, summary = id, title and severity badge, body = Locations list, *Why it matters*, *Recommended fix*, *Rule*; `open` on Critical and High; `<p>No findings.</p>` when there is none); *In good shape* (`ul`); *Hand-off* (the template's text, the two commands as `pre` blocks).
   - Tones — severity: Critical `badge--error`, High `badge--warning`, Medium `badge--info`, Low plain `badge`; conformance: met `badge--success`, partial `badge--warning`, not met `badge--error`, not verifiable plain `badge`; `badge--dot` in table cells.
2. Fill it from a realistic sample Markdown review (every severity, a conformance block, a generic in inline code) and build it with `new_report.py`.

### Acceptance criteria

- Every class the fragment uses exists in `html-report`'s `reference/components.md`; it has no `<style>`, `<script>`, `style=` attribute, colour value or reserved id.
- The filled sample builds with `wrote …` and no warning; `--dump-dom` shows the contents links for every `h2` and severity `h3`, and the Critical/High expanders open.
- Light and dark screenshots render the header, cards, tables, badges and expanders correctly; `--print-to-pdf` succeeds.
- The fragment's sections, order and text match `templates/report.md`.
- Both script suites still pass (34 + 51).

## PHASE02 — Wire /review to html-report

**Status:** DONE

### Steps

1. `skills/review-standards/SKILL.md`: rewrite *HTML rendering* — built with `html-report`'s `scripts/new_report.py` from `templates/report-content.html`; same findings, order and text; the exact command (`-t "Code review — <scope> — <date>"`, `-c <fragment in the scratchpad>`, `-o docs/review/<date>-<scope>.html`, `-f`, `--date <date>`); a warning means fix the fragment and rebuild; a refusal or no Python 3 skips the HTML with one console line and leaves the Markdown. Delete `templates/report.html`. Bump `metadata.version` to `2.0.0`. Keep the file ≤ 9,125 bytes.
2. `commands/review.md`: Phase 1 also loads `html-report` (for its build script; the fragment replaces its gather, plan and write steps); Phase 5 step 2 builds the HTML per the skill and prints the skip line when it cannot; *Rules* allow the fragment in the scratchpad and `html-report`'s build script; bump to `1.5.0`.
3. README: *Prerequisites* — Python also renders `/review`'s HTML report; *What to install* — `/review` needs `review-standards` and `html-report`; the `/review` section's "plus an HTML rendering" names `html-report`.
4. Walk `/review` Phase 5 on a sample Markdown report: write the fragment per the skill, run the documented command, check the output.

### Acceptance criteria

- No reference to `review-standards`' `templates/report.html` or its `{{placeholders}}` remains in `commands/`, `skills/` or the README.
- `SKILL.md` ≤ 9,125 bytes with valid frontmatter at `2.0.0`; `review.md` frontmatter valid at `1.5.0`; every path either names exists.
- The documented command, run as written on the sample, prints `wrote …` with no warning and overwrites on a rerun.
- README links resolve and its tables stay column-aligned.
- Both script suites still pass (34 + 51).

## Out of scope

- Changing the Markdown report, the finding shape or anything `/interview` and `/vibe` consume.
- Changing `html-report` (template, script or catalogue) or localizing its interface labels.
- A Markdown-to-HTML converter script, or headless rendering inside `/review`.
- Re-rendering existing `docs/review/*.html` files in other repositories.

## Decisions taken autonomously

| Question                                 | Chosen                                                                                                                                          | Why                                                                                                                                        | Alternatives rejected                                                                     |
|------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| How `review-standards` uses the template | `/review` loads `html-report` and builds with its `new_report.py`; `review-standards` ships a review content fragment                           | One template and one script: a fix to either lands once; the house already composes skills by name                                         | Copy the 200 KB template (and the script) into `review-standards` — two copies drift      |
| Fate of `templates/report.html`          | Deleted, replaced by `templates/report-content.html`                                                                                            | A fragment, not a page — the new name says so; one HTML look to maintain                                                                   | Keep it as the no-Python fallback (two renderings to keep in step)                        |
| Findings layout                          | One `h3` per severity in the contents; one expander per finding with its id, in an `expander-group` without `name`, `open` on Critical and High | The contents replace the old severity filter, which needs `<style>` the fragment may not carry; ids keep `#EXC-03` links working           | An `h3` per finding (a contents entry per finding); a flat list without severity headings |
| Severity badge tones                     | Critical error · High warning · Medium info · Low neutral                                                                                       | A red → amber → blue → grey gradient; green would read as "good"                                                                           | Low as success; Medium as accent                                                          |
| Conformance status tones                 | met success · partial warning · not met error · not verifiable neutral                                                                          | The template's status semantics (*On track* = success, *At risk* = warning, *Blocked* = error)                                             | Plain text statuses                                                                       |
| Who writes the fragment                  | Claude, from the Markdown report and the skeleton, as it does today                                                                             | The shape is fixed and small; no new code to maintain                                                                                      | A Markdown-to-HTML converter script with its own tests (gold-plating)                     |
| Captions on the review tables            | Fixed captions given by the skeleton                                                                                                            | `html-report` numbers and describes tables through `caption`; screen readers announce it                                                   | No captions (unnumbered, undescribed tables)                                              |
| Summary visuals                          | Four key-figure cards (Critical/High/Medium/Low) above the tally table                                                                          | The catalogue allows two to four cards; the table keeps the locations and total                                                            | Five cards with the total (over the catalogue's limit); table only                        |
| No Python 3, or the build refuses        | Keep the Markdown, skip the HTML, print one `review:` line                                                                                      | The Markdown is the source of truth; splicing by hand means reading the 200 KB template                                                    | Fail the review; hand-splice                                                              |
| Verification inside `/review`            | The script's `wrote` line and no warning; no headless render                                                                                    | `/review` runs only read-only git, `dotnet` and now the build script                                                                       | Headless Edge in every review                                                             |
| Versions                                 | `review-standards` 2.0.0; `/review` 1.5.0; `html-report` unchanged                                                                              | The skill removes a template and its placeholder contract (breaking); the command's arguments and outputs are unchanged (behaviour change) | `review-standards` 1.3.0; `/review` 2.0.0                                                 |
| Phasing                                  | Two phases: the fragment, then the wiring and docs                                                                                              | Each commit leaves the repository consistent: PHASE01 only adds a file                                                                     | One phase; three phases (a README-only phase is too small to review alone)                |
