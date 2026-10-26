---
name: dotnet-solution-setup
description: Use when creating a new .NET solution or project, adding a project to a solution, writing or editing csproj files, choosing target frameworks, or wiring application startup and hosting. Carries the ordered new-solution bootstrap checklist (which root file each skill owns, in creation order) and bundled .slnx / library .csproj / test .csproj / LICENSE.md templates.
---

# .NET solution & project setup

**Version: dotnet-solution-setup v6.**

## New solution bootstrap — the ordered checklist

Bootstrapping a solution spans three skills. This is the entry point: the full set of root artifacts, in creation order, each with the skill that owns it. Work top to bottom.

| Order | Artifact | Owner |
|---|---|---|
| 1 | `git init -b <branch>` (or an existing repo) | user / dev-workflow |
| 2 | `.gitignore`, `.gitattributes` | git-repo-hygiene |
| 3 | `.editorconfig` — the **full C#** one, not git-repo-hygiene's minimal line-endings file | dotnet-solution-config |
| 4 | `Directory.Build.props`, `Directory.Packages.props` | dotnet-solution-config |
| 5 | `global.json` — SDK pin **and** the MTP `test.runner` entry | dotnet-solution-config |
| 6 | `LICENSE.md` | **this skill** — `templates/LICENSE.md` |
| 7 | `README.md`, `RELEASENOTES.md` — created **empty** | created here, filled by dotnet-release |
| 8 | `<Solution>.slnx` | **this skill** — `templates/Solution.slnx` |
| 9 | `src/<Project>/<Project>.csproj` | **this skill** — `templates/library.csproj` |
| 10 | `tests/<Project>.UnitTests/<Project>.UnitTests.csproj` + one smoke test | **this skill** — `templates/test.csproj` / xunit-v3 |
| 11 | `docs/roadmap.md`, `docs/plan/`, `docs/done/` | dev-workflow |

`README.md` and `RELEASENOTES.md` exist from the first commit as **0-byte placeholders** — so the release phase has something to fill rather than something to invent.

**Appears later, not at bootstrap:** `docs/guides/` and `msiProfiles/` are created by dotnet-release, and the library's NuGet packaging metadata (`PackageId`, `Version`, `Description`, `PackageReadmeFile`/`PackageLicenseFile` and their packing `ItemGroup`, …) is added to the csproj at release time — which is why `templates/library.csproj` ships without it.

## Solution layout

- Solution format: **`.slnx`** (XML), not legacy `.sln`. The .NET 10 SDK's `dotnet new sln` emits `.slnx` by default; migrate existing files with `dotnet sln <file.sln> migrate` (keep only one of `.sln`/`.slnx` per directory).
- Three top-level directories at the solution root:
  - `src/` — production projects
  - `tests/` — test projects (xUnit v3, package `xunit.v3` 4.x — see xunit-v3)
  - `docs/` — markdown documentation

## Target frameworks

**The house modern-.NET set is `net10.0`** — every .NET **LTS** release still in support, never an STS (`net9.0`, `net11.0`). This section is the one place the set is stated: **dotnet-release** normalizes a library to it at release time, and **xunit-v3** test projects mirror it.

- **Review by: 2027-11-09.** .NET 12 (LTS) is due in November 2027 and joins the set when it ships; .NET 10's support ends 2028-11-14 (Microsoft's release metadata).
- **`net8.0` left the set** because .NET 8's support ends **2026-11-10**: nothing new targets it, and dotnet-release *proposes* dropping it from an existing library at its next release.
- An out-of-support TFM gets no security fixes, and an app or test project on one fails the zero-warnings build once the SDK lists it as end-of-life (`NETSDK1138` — checked for every project whose `OutputType` is not `Library`).

| Project type | TFM |
|---|---|
| Library | `netstandard2.0` + the house set — `netstandard2.0;net10.0`, as in `templates/library.csproj` (`netstandard2.0` for consumer reach, out-of-support runtimes included) |
| Application (console, worker, Avalonia, WPF) | the newest LTS alone — `net10.0` (WPF: `net10.0-windows`) |
| Tests | the house-set TFMs of the project under test — `net10.0` — under `tests/` (xunit-v3) |

A library narrows that set only when its purpose requires it, with the reason documented in a `.csproj` comment: the house set alone when a dependency or the API surface rules out `netstandard2.0` (an Avalonia 12 control library, framework-specific surface), or `netstandard2.0` alone for a small library that gains nothing from the modern targets. A `netstandard2.0` library using C# 14: compiler-only features (`field` keyword, extension blocks) work as-is; add PolySharp to polyfill compiler-known types before using `init`/`required` members or nullable-analysis attributes like `[NotNullWhen]`.

## csproj defaults (every project)

**These defaults belong in one `Directory.Build.props` at the solution root**, not copy-pasted into every `.csproj` — see dotnet-solution-config, which owns that file (`LangVersion`, `Nullable`, `TreatWarningsAsErrors`, `EnforceCodeStyleInBuild`, author metadata). Shown here as the effective per-project result:

```xml
<PropertyGroup>
  <LangVersion>14</LangVersion>
  <Nullable>enable</Nullable>
  <!-- at minimum: <WarningsAsErrors>nullable</WarningsAsErrors> -->
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  <ImplicitUsings>disable</ImplicitUsings>
</PropertyGroup>
```

- **Never enable `ImplicitUsings`** — every file declares its own `using` directives.
- No `!` null-forgiveness without a justified, commented reason.

## Bootstrapping — every app builds an IHost

All applications wire configuration, logging, lifetime, and DI through `Microsoft.Extensions.Hosting.IHost` from day one. Console apps and workers:

```csharp
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

public static class Program
{
    public static async Task Main(string[] args)
    {
        HostApplicationBuilder builder = Host.CreateApplicationBuilder(args);
        // builder.Services.AddSingleton<IClock, SystemClock>();

        using IHost host = builder.Build();
        await host.RunAsync();
    }
}
```

- `Host.CreateApplicationBuilder` returns `HostApplicationBuilder`: register via `builder.Services`, read config via `builder.Configuration`. There is **no `ConfigureServices` callback** — that belongs to the legacy `IHostBuilder` API (`Host.CreateDefaultBuilder`), which new code does not use.
- **GUI apps must run the UI framework's own lifetime** — `await host.RunAsync()` alone never shows a window. See avalonia and wpf for the exact wiring.
- Resolve the application's root type (main window, root ViewModel, primary service) from `host.Services` — never `new` it up.
- Long-running background work goes through `IHostedService`/`BackgroundService`, not ad-hoc `Task.Run` in `Main` (see dotnet-async).
- Bind configuration through `IOptions<T>`/`IOptionsMonitor<T>` — services don't read `IConfiguration` directly (see dotnet-di-design).

## Decisions to surface when scaffolding

Don't silently default these — ask or state the choice explicitly: deployment model (framework-dependent vs self-contained, trimming/NativeAOT) · installer/packaging (MSIX, zip, `dotnet tool`, NuGet package) · OS targets for GUI apps (Windows/Linux/macOS) · localization (`.resx`) · logging sinks and levels (`Microsoft.Extensions.Logging`) · licensing of NuGet dependencies.

## Common mistakes

| Mistake | Fix |
|---|---|
| `dotnet new sln` kept as `.sln` / new `.sln` files | `.slnx` |
| `Host.CreateDefaultBuilder(args).ConfigureServices(...)` | `Host.CreateApplicationBuilder(args)` + `builder.Services` |
| Library scaffolded as `net10.0` "because it's newest" | `netstandard2.0` + the house set (`templates/library.csproj`), unless a documented reason narrows it |
| A new project targeting an out-of-support or STS TFM (`net8.0`, `net9.0`, `net11.0`) | Only the house set (*Target frameworks*) — no security fixes, and an app/test project fails with `NETSDK1138` once the SDK marks it EOL |
| `<ImplicitUsings>enable</ImplicitUsings>` (template default) | Always `disable`, explicit usings per file |
| Tests scaffolded with `dotnet new xunit` (v2) | xUnit v3 (`xunit.v3` 4.x) per the xunit-v3 skill |
| Repeating `LangVersion` / `Nullable` / `ImplicitUsings` / `TreatWarningsAsErrors` in a `.csproj` | They live once in `Directory.Build.props` (dotnet-solution-config); a project csproj carries none of them |
| `<PackageReference Include="System.Buffers" />` referenced unconditionally on a multi-targeted library | It is framework-provided on net8.0+ — an unconditional reference raises **NU1510** and fails the zero-warnings build. Guard it with `Condition="'$(TargetFramework)' == 'netstandard2.0'"` |

## Bundled files

Copy each to its target path and fill the placeholders. **Create only if missing** — if the target file already exists, do not overwrite it; show a diff against the template and let the user decide what to merge.

- [`templates/Solution.slnx`](templates/Solution.slnx) — `.slnx` with `/src/` and `/tests/` solution folders (`{{PROJECT}}`).
- [`templates/library.csproj`](templates/library.csproj) — library on `netstandard2.0` + the house set, with the conditional `System.Buffers` / `PolySharp` groups; no packaging metadata (release-time).
- [`templates/test.csproj`](templates/test.csproj) — MTP-native xUnit v3 test project (`{{PROJECT}}`) on the house set, with the fixture copy-glob.
- [`templates/LICENSE.md`](templates/LICENSE.md) — MIT license text (`{{YEAR}}`, `{{AUTHORS}}`).

Neither csproj template carries a `Version=` attribute on a `PackageReference` — versions come from `Directory.Packages.props` under Central Package Management (dotnet-solution-config).

If an existing solution has its own layout or bootstrapping conventions, stay consistent with it and flag the divergence rather than silently mixing styles.
