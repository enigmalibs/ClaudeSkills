<!--
  Package README template. Copy into the target repo as the repository-root README.md
  (create only if missing — diff against an existing README, never clobber it; an empty file, such
  as the 0-byte placeholder dotnet-solution-setup creates at bootstrap, counts as missing and is
  filled) and fill:
    {{PACKAGE_ID}}     NuGet package id / repo-root title  e.g. Enigma.Core
    {{VERSION_MINOR}}  the X.Y used in the what's-new callout   e.g. 1.0
    {{TFM_LIST}}       supported target frameworks, prose form — the library's real TFMs, as in
                       its csproj, e.g. **.NET Standard 2.0** and **.NET 10.0**

  Keep it summary-length — this file is packed into the nupkg (PackageReadmeFile) and is the
  nuget.org landing page. The per-category guides under docs/guides/ carry the detail; the README
  states what the library is, the one idea a consumer must hold, and how to start.

  Link rule (correctness, not style): the packed README is rendered on nuget.org, where relative
  links into docs/ are dead. Link only to files that are packed or repo-root (LICENSE.md,
  RELEASENOTES.md), point at the guides in prose, and never use absolute GitHub URLs.
-->
# {{PACKAGE_ID}}

[![NuGet](https://img.shields.io/nuget/v/{{PACKAGE_ID}}.svg)](https://www.nuget.org/packages/{{PACKAGE_ID}})
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)

<!-- Intro: one paragraph. What the library is, and the single idea a consumer needs to hold —
     the idiom every part of the surface follows. No bullet list here. -->
One paragraph describing what {{PACKAGE_ID}} is and the one pattern the whole surface follows —
the idea a consumer has to hold to use anything in it. Name the primary dependency or runtime
foundation if there is one, and say whether it leaks onto the public surface.

> **What's new in {{VERSION_MINOR}}** — one-line highlight of this release. See
> [RELEASENOTES.md](RELEASENOTES.md).

## Features

<!-- One bullet per category the library actually has, each opening with a bold category name and
     naming the concrete capabilities. A summary, not a manual — the guides carry the detail. -->
- **First category** — the concrete capabilities it covers, named.
- **Second category** — the concrete capabilities it covers, named.
- **Third category** — the concrete capabilities it covers, named.

<!-- Optional: one ### subsection for a property that spans categories rather than belonging to
     any one of them (e.g. "Asynchronous, cancellable, observable"). Delete if there is none.

### Cross-cutting capability

Two or three sentences on the property that holds across the categories above and what it buys
the caller.
-->

## Installation

```bash
dotnet add package {{PACKAGE_ID}}
```

Targets {{TFM_LIST}}; built on <primary dependency + version>.

## Quick start

<!-- ONE short, real, compiling snippet showing the core idiom end to end (~10 lines). Not a tour.
     Every snippet is subject to the verification gate: it must match the real public API. -->
One sentence naming the steps the snippet shows:

```csharp
using System;
// … the full using block the snippet actually needs

// the core idiom, end to end, in about ten lines
```

## Documentation

<!-- Prose-only pointer. No clickable per-guide links, no absolute URLs — this file is packed. -->
Per-category guides — each with the supported <algorithms/operations>, the key types, and
copy-pasteable C# samples verified against the public API — live under `docs/guides/` in the
repository, indexed by `docs/guides/README.md`. They cover <the categories, listed in prose>.

## License

{{PACKAGE_ID}} is released under the [MIT License](LICENSE.md).
