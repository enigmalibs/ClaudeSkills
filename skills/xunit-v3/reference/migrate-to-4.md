# Migrating to 4.0 — xunit-v3 reference

Read this when a project is on xUnit v2, VSTest mode or `xunit.v3` 3.x and its migration is the work item. The core `SKILL.md` still applies: the packages and project setup, the `global.json` runner entry, running tests, parallelization and the v3 API notes.

## Runner & CI changes in 4.0

- **Report switches renamed** (MTP mode): `--report-ctrf` → `--report-xunit-ctrf`, `--report-junit` → `--report-xunit-junit`, `--report-nunit` → `--report-xunit-nunit`, `--report-xunit` → `--report-xunit-xml`. These **fail loudly** — an old name is rejected and the run exits non-zero having executed nothing.
- **Report file extensions changed:** `.junit` → **`.junit.xml`**, `.nunit` → `.nunit.xml`, `.xunit` → `.xunit.xml` (CTRF stays `.ctrf`). These **fail silently** — a CI artifact glob on an old extension matches nothing while the build stays green. This is the dangerous one: fix the globs at the same time as the switches.

## Migrating a 3.x project to 4.0

1. Bump `xunit.v3` to `4.0.0`; confirm the toolchain is SDK 8.0.400+ / VS 2022 17.11+ (Analyzers 2.0.0 needs Roslyn 4.11+).
2. Confirm every test TFM is `net8.0`+ (or `net472`).
3. Replace `coverlet.collector` with `Microsoft.Testing.Extensions.CodeCoverage`; update the coverage invocation (`--collect:"XPlat Code Coverage"` / `/p:CollectCoverage` no longer apply — use `dotnet test -- --coverage …`).
4. Rename `[assembly: CollectionBehavior(…)]` → `[assembly: Parallelization(…)]`: `DisableTestParallelization = true` → `Mode = ParallelMode.None`, `MaxParallelThreads` → `MaxThreads`. Add `using Xunit.v3;` and `using Xunit.Sdk;`.
5. Update CI report switch names **and** artifact globs (`.junit.xml`, `.nunit.xml`, `.xunit.xml`).
6. Drop any `xunit.v3.mtp-v1` reference — MTP v1 is gone at 4.x.
7. Note any Mono-hosted run: official support is discontinued.
8. Run the suite. Analyzers 2.0.0 diagnostics surface as warnings, which the house `TreatWarningsAsErrors` turns into build failures — triage them as part of the migration, not afterwards.

## Common stale v2 / 3.x-isms

| Wrong | Right (v4) | From |
|---|---|---|
| `<PackageReference Include="xunit" Version="2.x" />` | `xunit.v3` | v2 |
| `Microsoft.NET.Test.Sdk` + `xunit.runner.visualstudio` | `xunit.v3` alone + the `global.json` runner entry | v2 |
| Missing `<OutputType>Exe</OutputType>` or a hand-written `Program.Main` | Exe output; `Main` is generated | v2 |
| `using Xunit.Abstractions;` | `using Xunit;` | v2 |
| `Task IAsyncLifetime.InitializeAsync()` | `ValueTask` | v2 |
| `coverlet.collector` | `Microsoft.Testing.Extensions.CodeCoverage` | 3.x |
| `[assembly: CollectionBehavior(DisableTestParallelization = true)]` | `[assembly: Parallelization(Mode = ParallelMode.None)]` | 3.x |
| `[assembly: CollectionBehavior(MaxParallelThreads = n)]` | `[assembly: Parallelization(MaxThreads = n)]` | 3.x |
| `--report-junit` / `--report-ctrf` | `--report-xunit-junit` / `--report-xunit-ctrf` | 3.x |
| CI glob `**/*.junit` | `**/*.junit.xml` | 3.x |
| `xunit.v3.mtp-v1` | removed at 4.x — plain `xunit.v3` (MTP v2) | 3.x |
