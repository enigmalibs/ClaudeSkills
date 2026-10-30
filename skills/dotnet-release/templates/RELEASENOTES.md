<!--
  Release notes template. Copy into the target repo as the repository-root RELEASENOTES.md
  (create only if missing — diff against an existing file, never clobber it; an empty file, such as
  the 0-byte placeholder dotnet-solution-setup creates at bootstrap, counts as missing and is
  filled) and fill:
    {{PACKAGE_ID}}  NuGet package id / product name  e.g. Enigma.Core
    {{VERSION}}     the release X.Y.Z                e.g. 1.0.0

  Two variants follow — FIRST RELEASE and SUBSEQUENT RELEASE. Use one; delete the other.

  Newest-first: a subsequent release PREPENDS its section above the previous one. If the top
  section is headed "(unreleased)", RENAME it to "{{PACKAGE_ID}} v{{VERSION}} Release Notes"
  rather than adding a second block.

  Sub-sections appear only where non-empty, and always in the order given below.
  This file is repo-root and NOT packed (the packing ItemGroup carries README.md and LICENSE.md
  only): the packed README names it in plain text, never as a link, and nuget.org shows
  PackageReleaseNotes in its own Release Notes tab.
-->

<!-- ============================ VARIANT A — FIRST RELEASE ============================ -->

# {{PACKAGE_ID}} v{{VERSION}} Release Notes

The first public release of **{{PACKAGE_ID}}** — one or two sentences of positioning: what the
library is, the pattern its whole surface follows, and the constraint that shapes it (e.g. a
backing dependency that never appears on the public API).

## Feature overview

<!-- The same categories as the README's Features, at slightly more depth. -->
- **First category** — the concrete capabilities, named, with the details a README bullet omits.
- **Second category** — the concrete capabilities, named.
- **Third category** — the concrete capabilities, named.
- **Cross-cutting property** — the behaviour that holds across the categories above (async,
  cancellation, progress, thread-safety …), if there is one.

## Compatibility

- Targets **<TFM>**, **<TFM>**, and **<TFM>**.
- Built on **<primary dependency X.Y.Z>**.

## Version

- Initial release: **{{VERSION}}**.

<!-- ========================= VARIANT B — SUBSEQUENT RELEASE =========================
     Prepend this block above the previous release's section. Keep only the sub-sections that
     have content, in exactly this order.

# {{PACKAGE_ID}} v{{VERSION}} Release Notes

One-paragraph summary of what this release is about.

## New Features

- What was added, from the consumer's point of view.

## Fixes

- What was broken and now is not.

## Breaking Changes & Migration

- The break, then what a caller must change. Give the before/after where a signature moved.

## Dependencies

- `<Package>` **old → new**.
- `<Coupled ecosystem>` held back at **old** — bumped as a set, not one package at a time.

## Compatibility

- Target frameworks **old set → new set**.
- Dropping a TFM is a compatibility break — say so explicitly here, and under *Breaking Changes & Migration*.

## Version

- Released: **{{VERSION}}**.
-->
