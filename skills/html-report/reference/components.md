# Report components — markup catalogue

Markup and usage rules for everything the content region of a report can hold. Copy the snippets as they are. The template's stylesheet and script already handle the look, both themes, numbering, the table of contents, copy buttons and print.

## The content fragment

The fragment is what `new_report.py` puts between the template's `REPORT:CONTENT` markers: one document header, then one article. Nothing else — no `<html>`, `<head>`, `<body>`, `<style>` or `<script>`. The script sets the title in the browser tab, the top bar and the footer, and the footer's *Last updated* date, so don't write them yourself.

```html
<header class="doc-header">
  <p class="doc-header__eyebrow">Quarterly report</p>
  <h1 class="doc-title">IT Operations Review — Q3 2026</h1>
  <p class="doc-subtitle">Service levels, project portfolio and priorities for the last quarter.</p>
  <dl class="doc-meta">
    <div><dt>Author</dt><dd>Project Office</dd></div>
    <div><dt>Date</dt><dd><time datetime="2026-10-23">23 October 2026</time></dd></div>
    <div><dt>Version</dt><dd>1.0</dd></div>
    <div><dt>Status</dt><dd>Draft</dd></div>
  </dl>
</header>

<article class="doc" data-numbered>
  <h2>Summary</h2>
  <p class="lead">One or two sentences with the key message of the report.</p>
  …
</article>
```

- **Eyebrow** — a category of two or three words (*Audit report*, *Technical note*), shown as a pill. Optional.
- **Title** — the only `h1`, always `class="doc-title"`. Pass the same text, or a shorter form, to the script's `-t`.
- **Subtitle** — one sentence on what the report covers. Optional.
- **Metadata** — keep the `dl.doc-meta` structure with two to five entries that apply (author, date, version, status, client, reference…). Write dates in full, with a machine-readable `<time datetime>`.
- **`data-numbered`** on the article numbers the headings (1, 1.1, 1.1.1) in the text and in the contents by default. The reader can switch the numbers on or off with the top-bar button, and that choice is remembered. Leave the attribute out for short or informal documents.
- **`data-toc-title="…"`** on the article renames the contents box (default *Contents*), e.g. `Sommaire` for a French report.

## Headings

```html
<h2>Section</h2>
<h3>Sub-section</h3>
<h4>Part of a sub-section</h4>
<h5>Small uppercase label</h5>
<h3 data-no-toc>Heading kept out of the contents</h3>
<h2 id="risks">Risks</h2>
```

- Sections start at `h2`. Never skip a level going down (`h2` → `h4`).
- `h2`–`h4` feed the table of contents (a sticky sidebar on wide screens, a box after the header otherwise) and get a `#` link on hover. `h5` never appears in the contents.
- `data-no-toc` keeps a heading out of the contents. It then gets no number, no generated id and no `#` link.
- Ids are generated from the heading text: lower case, accents removed, hyphens (*Risks and issues* → `risks-and-issues`). Give an explicit `id` to any heading you link to with `<a href="#…">`, so the link survives a change of wording.
- Each `h2` gets an accent bar automatically. Don't add decorations or numbers yourself.

## Text

```html
<p class="lead">Opening paragraph, slightly larger — one per report, right after the first h2.</p>
<p>Body text with <strong>strong emphasis</strong>, <em>emphasis</em>, <a href="#risks">a link</a>,
  <mark>a highlighted passage</mark>, <small>small print</small>, <code>inline code</code>
  and keys such as <kbd>Ctrl</kbd> + <kbd>P</kbd>.</p>
```

- Keep paragraphs to three to five sentences.
- Use `mark` sparingly, for the one phrase a skimming reader must not miss.
- Links to web pages are fine; they don't affect offline rendering.

## Callouts

```html
<div class="callout callout--info" role="note">
  <svg class="icon callout__icon" aria-hidden="true" focusable="false"><use href="#icon-info"/></svg>
  <div class="callout__body">
    <p class="callout__title">Reporting period</p>
    <p>The figures cover January to September 2026.</p>
  </div>
</div>
```

| Tone    | Class              | Icon `href`     | Use for                                            |
|---------|--------------------|-----------------|----------------------------------------------------|
| Info    | `callout--info`    | `#icon-info`    | Context, scope, definitions, how to read a section |
| Success | `callout--success` | `#icon-success` | Results achieved, approvals, milestones            |
| Warning | `callout--warning` | `#icon-warning` | Risks, points to watch, deadlines, assumptions     |
| Error   | `callout--error`   | `#icon-error`   | Blockers, failures, decisions needed urgently      |

- The icon `href` always matches the tone. The icons live in the template; never paste SVG paths.
- The title is two to five words. The body is one to three short paragraphs, or a paragraph and a short list; links, lists and inline code are fine.
- Use at most one or two callouts per section, never two of the same tone in a row. A callout highlights the text; it doesn't replace it.

## Badges

```html
<span class="badge badge--success">On track</span>
<span class="badge badge--warning badge--dot">At risk</span>
<span class="badge">Draft</span>
<span class="badge badge--accent">New</span>
```

- Tones: `badge--info`, `badge--success`, `badge--warning`, `badge--error`, `badge--accent`. Plain `badge` is neutral grey.
- `badge--dot` adds a leading dot. Use it for statuses in tables and lists.
- Keep a badge to one or two words. Within a report, a given status always gets the same tone, e.g. *On track* and *Done* = success, *At risk* = warning, *Blocked* = error, *Planning* = info.
- Badges scale with the text around them, so they work in paragraphs, headings, expander summaries and table cells. A badge in a heading is left out of the contents and of the generated id.

## Figures

Every `figure` with a `figcaption` is numbered *Figure 1, 2…* automatically, in order of appearance, and the caption is shown below it.

Image (embedded, never linked):

```html
<figure>
  <img src="data:image/png;base64,…" alt="Description of what the image shows">
  <figcaption>Network architecture after the migration.</figcaption>
</figure>
```

Inline SVG illustration:

```html
<figure>
  <svg viewBox="0 0 600 260" role="img" aria-labelledby="fig-uptime-title">
    <title id="fig-uptime-title">Bar chart of monthly availability: July 99.95%, August 99.90%, September 99.98%.</title>
    <line class="fig-axis" x1="40" y1="220" x2="580" y2="220" stroke-width="1.5"/>
    <rect class="fig-accent" x="80" y="40" width="80" height="180" rx="6"/>
    <text class="fig-muted" x="120" y="242" font-size="13" text-anchor="middle">Jul</text>
    …
  </svg>
  <figcaption>Monthly availability of the production platform, Q3 2026.</figcaption>
</figure>
```

- **Caption** — the description only, as a sentence, with units and period. Never write "Figure 1:" yourself; the number is added.
- **SVG** — always a `viewBox` and no `width`/`height`: the figure scales to the column. Add `role="img"` and a `<title>` whose unique `id` is referenced by `aria-labelledby`, describing the data for screen readers. Use a 600-unit-wide viewBox and font sizes of 12–16 so labels stay legible.
- **Colours** come from these classes. They follow the light and dark themes and print in the light palette; never hard-code colours.

| Class             | Paints                                     | Typical use                       |
|-------------------|--------------------------------------------|-----------------------------------|
| `fig-text`        | fill: main text colour                     | Values, labels in boxes           |
| `fig-muted`       | fill: secondary text colour                | Axis labels, legends, notes       |
| `fig-grid`        | stroke: light rule                         | Grid lines                        |
| `fig-axis`        | stroke: strong rule                        | Axes, arrows, connectors          |
| `fig-accent`      | fill: accent blue                          | Main data series                  |
| `fig-accent-soft` | fill: accent tint, stroke: accent          | Forecast, secondary series, boxes |
| `fig-info`        | fill: info tint, stroke: info accent       | Boxes in diagrams                 |
| `fig-success`     | fill: success tint, stroke: success accent | Boxes in diagrams                 |
| `fig-warning`     | fill: warning tint, stroke: warning accent | Boxes in diagrams                 |
| `fig-error`       | fill: error tint, stroke: error accent     | Boxes in diagrams                 |

  Set `stroke-width` as an attribute, and `fill="none"` on lines and arrows. A class can go on a `<g>` to paint a whole group. Fonts are inherited from the document.
- Prefer a simple chart with few labels to a dense one: the figure shrinks on phones.

## Tables

```html
<div class="table-wrap">
  <table>
    <caption>Project portfolio at 30 September 2026. Budget and spend in CHF thousands.</caption>
    <thead>
      <tr><th scope="col">Project</th><th scope="col">Status</th><th scope="col" class="num">Budget</th><th scope="col" class="num">Spent</th></tr>
    </thead>
    <tbody>
      <tr><th scope="row">Client portal</th><td><span class="badge badge--success badge--dot">On track</span></td><td class="num">420</td><td class="num">265</td></tr>
      <tr><th scope="row">Billing automation</th><td><span class="badge badge--error badge--dot">Blocked</span></td><td class="num">150</td><td class="num">92</td></tr>
    </tbody>
    <tfoot>
      <tr><th scope="row">Total</th><td></td><td class="num">570</td><td class="num">357</td></tr>
    </tfoot>
  </table>
</div>
```

- Always wrap the table in `div.table-wrap`, so a wide table scrolls sideways within its frame instead of widening the page.
- `caption` is the **first child** of `table`. It is numbered *Table 1, 2…* and shown below the table. Write the description only, units included.
- Use `th scope="col"` for column headers and `th scope="row"` for the first cell of each row.
- Put `class="num"` on every numeric cell **and** its column header: they are right-aligned with tabular figures. Format numbers consistently (`1,755`, `63%`, `—` for not applicable).
- Add a `tfoot` only for a total or summary row that really adds up.
- Up to about 8 columns read well on screen and on A4. Split larger tables.

## Key figures

```html
<dl class="kpis">
  <div class="kpi">
    <dt class="kpi__label">Revenue (CHF)</dt>
    <dd class="kpi__value">2.8 M</dd>
    <dd class="kpi__delta kpi__delta--up">+14% vs 2025</dd>
  </div>
  <div class="kpi">
    <dt class="kpi__label">Margin</dt>
    <dd class="kpi__value">18.4%</dd>
    <dd class="kpi__delta kpi__delta--down">−1.1 pt vs 2025</dd>
  </div>
</dl>
```

- Use two to four cards, near the top of the report or of a section.
- The label is one or two words, with the unit in brackets. Keep the value short (`2.8 M`, `46`, `4.6 / 5`): long values wrap.
- `kpi__delta` is optional. `--up` shows a green ▲ and `--down` a red ▼; with no modifier it is neutral grey. Use a real minus sign (`−`) and always name the reference (*vs 2025*, *vs target*).
- The modifiers tie direction to judgement (up = good, down = bad). When a rise is bad (incidents, costs) or a fall is good, leave the delta neutral and say it in words: `+3 vs Q2, above target`.

## Quotes

```html
<figure class="quote">
  <blockquote>
    <p>The new portal halved the time we spend on monthly reporting.</p>
  </blockquote>
  <figcaption><cite>Head of Finance, client steering committee</cite></figcaption>
</figure>

<blockquote>
  <p>A short quotation without a source.</p>
</blockquote>
```

- `figure.quote` is not numbered; its `figcaption` gives the source.
- Quote people only from material you were given. Never invent a quotation or its source.

## Code

```html
<pre><code>git switch -c feature/new-portal
dotnet test --configuration Release</code></pre>

<pre data-no-copy><code>Output shown for reference only</code></pre>
```

- Escape `&`, `<` and `>` inside code (`&amp;`, `&lt;`, `&gt;`).
- Start the code right after `<code>` and keep it flush left: whitespace inside `pre` is shown as is.
- Every `pre` gets a **Copy** button automatically: it shows on hover or keyboard focus, and always on touch screens. `data-no-copy` on the `pre` leaves it out.
- Code blocks scroll sideways on narrow screens and wrap when printed.

## Expanders

```html
<details class="expander">
  <summary>Methodology and data sources</summary>
  <div class="expander__body">
    <p>Figures come from the finance ledger, closed on 30 September 2026.</p>
  </div>
</details>

<div class="expander-group">
  <details class="expander" name="faq">
    <summary>Why is the migration at risk?</summary>
    <div class="expander__body"><p>Spend runs ahead of progress.</p></div>
  </details>
  <details class="expander" name="faq" open>
    <summary>Who approves the revised estimates?</summary>
    <div class="expander__body"><p>The steering committee, on 18 November 2026.</p></div>
  </details>
</div>
```

- An expander tucks away detail that not every reader needs — methodology, raw figures, long lists, reference material — behind a one-line summary. The key messages stay outside it.
- Keep the summary short and specific, so the reader can decide whether to open it. A badge may follow the summary text.
- The body takes any other component: paragraphs, lists, tables, code (with its copy button), figures.
- `open` shows it open when the page loads.
- `expander-group` joins several into one list (questions and answers, appendices). Give them the same `name` and opening one closes the others.
- It is a native `details` element: it works without the script, find-in-page searches its hidden content, and a link to an id inside it opens it. Printed pages show every expander open.

## Lists and checklists

```html
<ul>
  <li>Point</li>
  <li>Point with detail
    <ul><li>sub-point</li></ul>
  </li>
</ul>

<ol>
  <li>First step</li>
  <li>Second step</li>
</ol>

<ul class="checklist">
  <li class="is-done">Figures reconciled</li>
  <li>Summary approved</li>
</ul>
```

- Use `ul` for related points and `ol` for sequences and rankings. Nest at most one level.
- A checklist shows progress: `is-done` items get a ticked box and muted text.

## Separators

```html
<hr>
<hr class="separator separator--dotted">
<div class="separator separator--label" role="separator" aria-label="Appendices"><span>Appendices</span></div>
```

- `<hr>` marks a change of topic inside a section. The dotted variant is a lighter pause. The labelled one introduces a part (*Appendices*, *Detailed findings*); keep its `aria-label` identical to the visible label.
- Headings remain the structure, so use separators sparingly.

## Two columns

```html
<div class="grid-2">
  <div>
    <h5>Strengths</h5>
    <ul><li>…</li></ul>
  </div>
  <div>
    <h5>Watch points</h5>
    <ul><li>…</li></ul>
  </div>
</div>
```

- Exactly two children, each short (a label and a list, a small figure, a callout). They stack on narrow screens.

## Printing

Readers print or save as PDF from the top-bar button or with <kbd>Ctrl</kbd> + <kbd>P</kbd>. The print layout uses A4 and the light theme, with page numbers. It leaves out the top bar, the contents, the footer and the copy buttons, opens every expander, and keeps callouts, figures, cards and table rows whole. Nothing in the fragment needs to change for print.

## Do not

- Write `<style>`, `<script>`, `style="…"` attributes or colour values. The template provides all styling, and hard-coded colours break the dark theme.
- Link images, fonts, stylesheets or scripts from the web. Embed images as inline SVG or `data:` URIs.
- Add a second `h1`, number headings, figures or tables by hand, or write a table of contents.
- Use the template's own ids: `top`, `content`, `toc`, `toc-title`, `toc-toggle`, `numbering-toggle`, `theme-toggle`, `print-button`, `report-styles`, `report-fonts`, or any id starting with `icon-`.
