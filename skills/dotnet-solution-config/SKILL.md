---
name: dotnet-solution-config
description: Use when setting up a .NET solution's shared root config — the full C# .editorconfig (code style, naming, analyzer severities), Directory.Build.props (solution-wide build defaults), Directory.Packages.props (Central Package Management), and global.json (SDK pin + the Microsoft Testing Platform test runner).
---

# .NET solution shared config

**Version: dotnet-solution-config v6.**

Give a .NET solution one authoritative code-style file and centralized build/package defaults at the solution root.

## When to use

- A new or existing .NET solution that wants one shared code-style file plus centralized build and package-version defaults across every project.
- Adding any one of the three files below to a solution that is missing it.
- Pinning the SDK, or switching `dotnet test` to the Microsoft Testing Platform, via a root `global.json`.

**Not for:** `.gitignore` / `.gitattributes` / CRLF line-ending normalization (see git-repo-hygiene) · per-project scaffolding, target frameworks, or IHost wiring (see dotnet-solution-setup).

## The three files

All three live at the **solution root**, beside the `.slnx`:

| File | Purpose | Source |
|------|---------|--------|
| `.editorconfig` | Full C# code style + naming conventions + analyzer severities, plus LF/charset/final-newline for all files. The single authoritative style file. | `templates/editorconfig` |
| `Directory.Build.props` | Solution-wide csproj defaults (`LangVersion`, `Nullable`, `ImplicitUsings`, `TreatWarningsAsErrors`, `EnforceCodeStyleInBuild`) + author metadata. | `templates/Directory.Build.props` |
| `Directory.Packages.props` | Central Package Management skeleton — one place for every package version. | `templates/Directory.Packages.props` |

A fourth file, `global.json`, lives at the same root and belongs to the same config family, but is **not** one of the three core files — see *global.json* below.

**Where this skill sits in the bootstrap order:** `dotnet-solution-setup`'s **New solution bootstrap** checklist is the single entry point for scaffolding a solution from scratch — it names every root artifact, its owning skill, and the creation order. This skill owns steps 3–5 of that checklist (`.editorconfig`, the two props files, `global.json`); `git-repo-hygiene` comes before it, and the projects come after.

## Workflow — create only if missing

For each of the three files, in the target solution root:

1. If the file **does not exist**, copy the matching template to its target name: `templates/editorconfig` → `.editorconfig`, `templates/Directory.Build.props` → `Directory.Build.props`, `templates/Directory.Packages.props` → `Directory.Packages.props`.
2. If the file **already exists**, do **not** overwrite it. Report that it exists and show a diff against the template so the user decides what (if anything) to merge.
3. In the freshly copied `Directory.Build.props`, fill the `{{AUTHORS}}` / `{{YEAR}}` placeholders.
4. Same rule for `global.json` (no bundled template — it's four lines, shown below): create it if missing, diff if present.

Never clobber an existing config — an established solution's `.editorconfig` or props often carry project-specific rules.

## Directory.Build.props

MSBuild imports `Directory.Build.props` into every project under the solution root automatically, so these defaults live in **one** place instead of being repeated in every `.csproj`:

- `LangVersion` / `Nullable` — the C# language level and nullable context for the whole solution.
- `ImplicitUsings` — always `disable`; every file declares its own `using` directives (see dotnet-solution-setup).
- `TreatWarningsAsErrors` — warnings fail the build everywhere (library, CLI, Desktop, tests).
- `EnforceCodeStyleInBuild` — the warning-level `.editorconfig` rules are checked at build time, not just in the IDE.
- `Authors` / `Copyright` — shared package/assembly metadata (the parameterized placeholders).

This is the single source of truth for these values — they do **not** belong in individual csproj files. (dotnet-solution-setup defers here for shared csproj defaults.)

## Central Package Management

`Directory.Packages.props` centralizes every dependency version:

- `<ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>` turns CPM on.
- Each version is declared **once**, centrally, as `<PackageVersion Include="Foo" Version="1.2.3" />`.
- Project `.csproj` files reference packages **without** a `Version`: `<PackageReference Include="Foo" />`. The version comes from the central file, so shared dependencies can't drift between projects.
- **Version-coupled ecosystems** are bumped **together**, never one package at a time — mixing versions within a set breaks the build. This is the one list; other skills point here instead of restating it:
  - **Avalonia** — `Avalonia`, `Avalonia.Desktop`, `Avalonia.Themes.Fluent`, `Avalonia.Fonts.Inter` and `Avalonia.Headless.XUnit` share one exact version. The packages built on it, `Enigma.Avalonia.Desktop` and `Enigma.Icons.Avalonia`, declare an Avalonia floor: move them with the set, and never pin the set below a floor — restore fails with NU1605 (package downgrade), which the SDK treats as an error.
  - **Not coupled:** `CommunityToolkit.Mvvm` and `AvaloniaUI.DiagnosticsSupport` do not depend on Avalonia and version on their own, within any floor a dependent declares (`Enigma.Avalonia.Desktop` needs a minimum `CommunityToolkit.Mvvm`).

  The template's Desktop group is the one place the Avalonia version is pinned, and it keeps the set together so it can be held back until it moves as a unit.

The template ships commented example groups (Core / App hosting / CLI / Desktop / Tests); uncomment and fill only the ones the solution needs. App hosting (`Microsoft.Extensions.Hosting`) is its own group because every application — CLI, worker or Desktop — builds an `IHost`.

The **Tests** group is MTP-native: `xunit.v3` plus `Microsoft.Testing.Extensions.CodeCoverage` for coverage (recommended, included by house default — see xunit-v3) — and **no `Microsoft.NET.Test.Sdk`**, which is VSTest-era boilerplate that breaks the Microsoft Testing Platform (see xunit-v3). The **Core** group's `System.Buffers` / `PolySharp` entries exist to back the *conditional* `netstandard2.0`-only `PackageReference`s in `dotnet-solution-setup/templates/library.csproj`; drop them for a library that doesn't multi-target `netstandard2.0`.

## global.json

`global.json` sits at the solution root beside the three files above. It carries two independent things:

```json
{
  "sdk": { "version": "10.0.100", "rollForward": "latestFeature" },
  "test": { "runner": "Microsoft.Testing.Platform" }
}
```

- **`sdk`** — pins the SDK so every machine and CI agent builds with the same toolchain. `rollForward: latestFeature` accepts a newer feature band of the same major version rather than failing on an exact-version mismatch.
- **`test`** — opts `dotnet test` into the **Microsoft Testing Platform** (MTP) instead of VSTest. Required for an xUnit v3 test project; **xunit-v3** owns the runner entry and the project side of it.

**Invocation:** how `dotnet test` takes a solution in MTP mode (`--solution`) is stated once, in xunit-v3's *Running tests*.

## Cross-references

- **git-repo-hygiene** — `.gitignore`, `.gitattributes`, and line-ending (CRLF↔LF) normalization. Its minimal line-endings-only `.editorconfig` is for text-only / non-C# repos; a .NET solution uses the full `.editorconfig` here instead (a strict superset).
- **dotnet-solution-setup** — solution/project layout, target frameworks, and IHost bootstrapping. Its **New solution bootstrap** checklist is the ordered entry point for a from-scratch solution and says which skill owns each root file; it also bundles the `.slnx`, library/test `.csproj` and `LICENSE.md` templates.
- **xunit-v3** — the test-project packages that go in the CPM file's Tests group, and the `global.json` `test.runner` entry.
- **dotnet-release** — consumes `Directory.Packages.props` when updating dependency versions.

## Bundled files

- [`templates/editorconfig`](templates/editorconfig) — full C# code style, naming, and analyzer severities (+ LF/charset).
- [`templates/Directory.Build.props`](templates/Directory.Build.props) — solution-wide build defaults + author-metadata placeholders.
- [`templates/Directory.Packages.props`](templates/Directory.Packages.props) — CPM skeleton with commented example groups.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Naming a bundled template `.editorconfig` (with a dot) | Keep bundled names un-dotted (`templates/editorconfig`); copy to the dotted name at the target. |
| Overwriting a solution's existing `.editorconfig` / props | Create only if missing; diff, don't clobber. |
| Keeping a separate code-style `.editorconfig` per project or split across skills | One authoritative `.editorconfig` at the solution root. |
| Repeating `LangVersion` / `Nullable` / `ImplicitUsings` / `TreatWarningsAsErrors` in every csproj | Put them once in `Directory.Build.props`. |
| Adding `Version="..."` to a project `<PackageReference>` under CPM | The version lives centrally in `<PackageVersion>`; the reference carries none. |
| Bumping one package of the Avalonia set individually, or pinning it below an Enigma package's floor | Bump the coupled set together (*Central Package Management*); a pin below a floor fails restore with NU1605. |
| `Microsoft.NET.Test.Sdk` in the CPM Tests group | VSTest-era boilerplate that breaks MTP — `xunit.v3` (+ the house-default `Microsoft.Testing.Extensions.CodeCoverage`) only. |
| `coverlet.collector` in the CPM Tests group | A VSTest data collector — MTP v2 (xunit.v3 4.0) does not host it, so coverage silently collects nothing while the build stays green. Use `Microsoft.Testing.Extensions.CodeCoverage`. |
| `global.json` with only the `sdk` pin, for a solution with xUnit v3 tests | Add `"test": { "runner": "Microsoft.Testing.Platform" }` too, or `dotnet test` falls back to VSTest. |
If an existing solution already has its own root config, stay consistent with it and flag the divergence rather than silently mixing styles.
