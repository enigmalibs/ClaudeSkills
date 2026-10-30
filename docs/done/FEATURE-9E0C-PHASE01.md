# FEATURE-9E0C-PHASE01 — Review content fragment

## Summary

Adds `skills/review-standards/templates/report-content.html`: the content fragment `/review` will fill and build with `html-report`'s `new_report.py`. It replaces the old page's `{{placeholders}}` and its own CSS (the switch itself is PHASE02).
- **Leading comment** — the fill rules: Markdown text only, HTML-escaped (C# generics included), no `{{` left; repeated blocks; which sections drop; the tone tables. It is never copied into a report.
- **Document header** — eyebrow *Code review*, the Markdown title as the `h1`, its "Written by …" line as the subtitle, and Scope, Revision, Date and Findings as the metadata.
- **Article** — one `h2` per Markdown section, in order:
  - Baseline, Summary and Plan conformance tables, captioned (so numbered), with `scope` headers and `num` cells;
  - four severity key-figure cards;
  - severity and conformance badges;
  - one `h3` per severity under *Findings* — the contents give the severity navigation the old CSS filter gave;
  - one expander per finding, carrying the finding's id, `open` for Critical and High;
  - the hand-off commands as code blocks with copy buttons.

## Files/modules touched

- Created: `skills/review-standards/templates/report-content.html`
- Modified: `docs/roadmap.md`, `docs/plan/FEATURE-9E0C.md` (statuses)
- Created: `docs/done/FEATURE-9E0C-PHASE01.md`

## Deviations & follow-ups

- None from the plan. The fragment is unused until PHASE02 wires `/review` to it; until then `templates/report.html` stays the rendering `/review` uses.

## Decisions taken at build time

| Question                                    | Chosen                                                                                            | Why                                                                                                                                                |
|---------------------------------------------|---------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| A finding's heading in the expander summary | `<code>KEY-NN</code>`, the title in a `<span>`, then the severity badge                           | The summary is a flex row: an unwrapped title with inline code splits into separate spaced items (seen on `ASYNC-01`). The badge replaces `[High]` |
| Labels inside a finding                     | `<p><strong>Locations</strong></p>` and `<strong>Why it matters</strong> — …`, as in the Markdown | An `h5` label under an `h3` skips `h4`, which the catalogue forbids; the Markdown uses bold too                                                    |
| Criterion cell                              | `th scope="row"`                                                                                  | The catalogue's rule for a row's first cell                                                                                                        |
| Placeholder syntax                          | `{{…}}`, with "No `{{` may be left"                                                               | `report.md`'s `<…>` placeholders would read as tags in HTML; the old HTML template used `{{…}}`                                                    |
| Header metadata                             | Scope, Revision (`branch @ sha`), Date, Findings (total)                                          | Four of the catalogue's two to five entries; the reviewer's first questions                                                                        |
| Heading numbers                             | No `data-numbered`                                                                                | The Markdown has none; the reader can still switch them on                                                                                         |

## Build/test evidence

**Run baseline** (on `feature/2026-10-30-review-html-report` @ `d61a703`, before the first dev branch): no build step; `py -3 -B -m unittest discover -s skills/html-report/scripts` — 34 tests OK; `… -s skills/dev-workflow/scripts` — 51 tests OK. Later done docs of this run cite it.

- **Catalogue conformance** (script over the skeleton, comments stripped): 21 classes, all present in `html-report`'s `reference/components.md`. No `<style>`, `<script>`, `style=`, colour value, external URL or `src`; no reserved id; one `h1`.
- **Sections** — the seven `h2` texts equal `templates/report.md`'s `##` headings, in order.
- **Sample** — a filled sample covering every severity (6 findings, 12 locations), a 4-criterion conformance block with all four statuses, and the C# generics `Task<User>` and `ILogger<LoginService>` in inline code, escaped in the fragment:
  - `new_report.py -t "Code review — feature-3a7f — 2026-10-30" -c content.html -o … -f --date 2026-10-30` printed `wrote …`, with no warning.
  - Headless Edge `--dump-dom`: the contents list every `h2`, the work item `h3` and the four severity `h3`s; the Critical and High expanders are `open`, the Medium and Low ones closed.
  - Screenshots, light (full report) and dark (findings): header, cards, tables, badges, expanders and code render correctly.
  - `--print-to-pdf`: 5 A4 pages.
- **Suites after the change**: 34 + 51 tests OK.
- **Documentation sweep** — nothing stale: the file is not referenced yet (PHASE02 does that), and the README's tree does not list `templates/`.
