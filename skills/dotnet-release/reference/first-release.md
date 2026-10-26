# First release — dotnet-release reference

Read this before a **first release** — no version of the package is on nuget.org yet — or when pack-verify finds package metadata missing or a `.snupkg`. The core `SKILL.md` still applies: the execution boundary, pack-verify, the release documents, the NuGet refresh and the runbook.

## First release steps

1. **Package metadata** — fill all 12 properties and the packing `ItemGroup`, and confirm `GeneratePackageOnBuild` is off. See *Packable-library prerequisites*.
2. **Third-party license audit** — confirm every **runtime** dependency's license permits redistribution, and that the package's own `LICENSE.md` is present, correct and packed. **Test-only and compile-only packages don't ship**, so they are out of scope for the audit — the distinction is what makes it tractable:

   | Dependency | Kind | Ships? |
   |---|---|---|
   | `BouncyCastle.Cryptography` (MIT) | runtime, all TFMs | **yes** — audit it |
   | `System.Buffers` (MIT) | runtime, `netstandard2.0` only | **yes** — audit it |
   | `PolySharp` (MIT) | compile-only, `PrivateAssets=all` | no — not redistributed |
   | `xunit.v3`, `Microsoft.Testing.Extensions.CodeCoverage` | test-only | no — never in the package |

   (Enigma.Core's actual audit, as the worked example.) **Record the findings in the completion doc.** This step is **first release only** — it is not repeated on routine bumps.
3. **Author the release documents** from the templates — `README.md`, `RELEASENOTES.md` (first-release variant), the per-category guides and their index, and `SECURITY.md`. See `SKILL.md` *Release documents*, and *Writing the release documents the first time* below.
4. **`docs/RELEASE.md`** from [`templates/RELEASE.md`](../templates/RELEASE.md), placeholders filled.

## Packable-library prerequisites

Before the first release (or when verifying an existing one), the library csproj must carry all **12** of these:

| | Property | Purpose |
|---|---|---|
| 1 | `PackageId` | The published package name. |
| 2 | `Version` | The release `X.Y.Z` (also `SKILL.md` *Routine release* step 1, on every release). |
| 3 | `Title` | Short display name — the nuget.org heading. |
| 4 | `Description` | One-paragraph feature summary; nuget.org renders a package badly without it. |
| 5 | `PackageTags` | Space-separated search terms. |
| 6 | `PackageReadmeFile` | `README.md` — plus the packing `ItemGroup` below. |
| 7 | `PackageLicenseFile` | `LICENSE.md` — plus the packing `ItemGroup` below. |
| 8 | `RepositoryUrl` | Source repository. |
| 9 | `RepositoryType` | `git`. |
| 10 | `PackageProjectUrl` | Project landing page. |
| 11 | `PackageReleaseNotes` | Prose mirroring the top of `RELEASENOTES.md` — see `SKILL.md` *Routine release* step 2. |
| 12 | `GenerateDocumentationFile` | `true` — ships the XML doc file consumers get IntelliSense from. |

Plus two structural requirements:

- The **packing `ItemGroup`** — `PackageReadmeFile` / `PackageLicenseFile` name the files; this is what actually puts them in the package:
  ```xml
  <ItemGroup>
    <None Include="..\..\README.md" Pack="true" PackagePath="\" />
    <None Include="..\..\LICENSE.md" Pack="true" PackagePath="\" />
  </ItemGroup>
  ```
- **`GeneratePackageOnBuild` OFF** (absent, or `false`) — a publishable library is packed explicitly by the release step, never on every local build, consistent with the print-don't-run boundary.
- **No symbol properties** — `IncludeSymbols`, `SymbolPackageFormat`, `PublishRepositoryUrl`, and `EmbedUntrackedSources` must all be absent (see *Symbols — never shipped* below).

**dotnet-solution-setup**'s [`templates/library.csproj`](../../dotnet-solution-setup/templates/library.csproj) deliberately omits this whole block: the packaging metadata is added **here, at release time**, not at bootstrap. A library that has never been released will be missing all 12 — that is expected, not drift.

### Symbols — never shipped

**House rule: no symbol package.** A release ships exactly one file, the `.nupkg`. `dotnet pack` already behaves this way by default, so the rule is about *not* opting in:

- **Never add** `IncludeSymbols`, `SymbolPackageFormat`, `PublishRepositoryUrl`, or `EmbedUntrackedSources` to a packable csproj, and never suggest them — not as an option, not as a "consider this" aside.
- **Never pass** `--include-symbols` / `-p:IncludeSymbols=true` to `dotnet pack`, and never add a `dotnet nuget push` line for a `.snupkg`.
- **If an existing csproj carries any of them**, that is drift: report it and remove the properties so the next pack emits only the `.nupkg`.
- **Pack-verify asserts it** (`SKILL.md`) — a `.snupkg` beside the `.nupkg` means the opt-in leaked back in.

`GenerateDocumentationFile` (property 12) stays on — the XML doc file ships *inside* the `.nupkg` and is unrelated to symbols.

## Writing the release documents the first time

The release documents themselves are `SKILL.md`'s *Release documents*; this is what only the first one needs.

### README badges

**Badges** — the house set is exactly two, under the title, in this order:

```markdown
[![NuGet](https://img.shields.io/nuget/v/<PackageId>.svg)](https://www.nuget.org/packages/<PackageId>)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)
```

A **Downloads** badge (`nuget/dt`) exists if it is ever wanted, but it is not part of the house set and is **not offered**: on a fresh package it advertises a low count, which is a negative signal.

### Community files

- **`SECURITY.md`** — **offer** it from [`templates/SECURITY.md`](../templates/SECURITY.md) for any package published publicly.
- **`CONTRIBUTING.md`** — not part of the house set; add only on request.
- **`LICENSE.md`** — owned by **dotnet-solution-setup** (written at bootstrap from its `templates/LICENSE.md`); this skill only **verifies** it — step 2, prerequisite 7 and pack-verify.

## The shape of a first-release work item

**First release — 4 phases:**

| Phase | Content |
|---|---|
| PHASE01 | Package metadata & build config + the third-party license audit |
| PHASE02 | Per-category guides + their index |
| PHASE03 | Summary README + release notes + `PackageReleaseNotes` + community files |
| PHASE04 | `docs/RELEASE.md` + pre-flight + pack-verify + the printed runbook |

The first-release split is not arbitrary — two ordering constraints fix it:

- **Metadata before pack-verify.** There is nothing valid to pack until the 12 properties and the packing `ItemGroup` are in place, so the verify step cannot move earlier.
- **Guides before the README.** The README's *Documentation* section points at the guides and summarises what they cover; writing it first means writing it twice.

Practical note: a doc-only phase still **keeps the Release build green** whenever it touches the csproj — `PackageReleaseNotes` and `Description` are csproj edits even in a "documentation" phase.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `GeneratePackageOnBuild` left on for a publishable library | Turn it off; pack explicitly in the release step. |
| Publishing a package with no `Description` or `Title` | Both are required metadata; nuget.org renders the package badly without them. All 12 properties, every time. |
| Shipping or offering a symbol package — `IncludeSymbols` / `SymbolPackageFormat` / `--include-symbols`, or a `.snupkg` push line | House rule: releases ship the `.nupkg` only. Never opt in, never suggest it; strip the properties if an existing csproj has them. |
| Running the license audit on test-only packages, or skipping it on runtime ones | Audit what ships: runtime dependencies. Compile-only (`PrivateAssets=all`) and test-only packages are not redistributed. |
