<!--
  Guides index template. Copy into the target repo as docs/guides/README.md
  (create only if missing — diff against an existing index, never clobber it) and fill:
    {{PACKAGE_ID}}  NuGet package id / product name  e.g. Enigma.Core

  This file is repo-only — it is NOT packed into the nupkg (unlike the root README), so relative
  links to the sibling guides are correct HERE and resolve when browsing on GitHub. The packed
  root README must point at the guides in prose instead.

  The index stands alone: repeat the core idiom rather than assuming the reader arrived from the
  README. Group the guides under ## theme headings; one theme is fine for a small library.
  The number of guides follows the library's categories — there is no target count.
-->
# {{PACKAGE_ID}} — Guides & Samples

Per-category guides for **{{PACKAGE_ID}}**, <one clause on what the library is>. <Restate the core
idiom in one or two sentences — the pattern every category follows, and how the types are obtained
(`new` vs dependency injection), so this page stands on its own.>

Each guide follows the same shape — **supported <algorithms/operations> → key types →
copy-pasteable usage samples** — and every snippet targets the real public API.

## <First theme>

- [<Guide title>](<file>.md) — <one-line scope: the concrete capabilities the guide covers>.
- [<Guide title>](<file>.md) — <one-line scope>.

## <Second theme>

- [<Guide title>](<file>.md) — <one-line scope>.

## <Third theme>

- [<Guide title>](<file>.md) — <one-line scope>.
