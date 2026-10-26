# Style — review-standards reference

Read this when reviewing `STYLE`. The house skills still apply and are cited, not repeated: dotnet-solution-config (the solution-root `.editorconfig` is the one authoritative style file; `TreatWarningsAsErrors` and `EnforceCodeStyleInBuild` are on) and dotnet-solution-setup (`ImplicitUsings` disabled; every file declares its own usings; the four build properties live once in `Directory.Build.props`). The reviewed solution's own `.editorconfig` wins over any opinion here: read it first and flag deviations from *it*. Most findings here are Low; group aggressively.

## Naming

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Deviates from the solution's `.editorconfig` | its `dotnet_naming_*` rules vs the code (`_camelCase` fields, `PascalCase` members, `I`-prefixed interfaces, `Async` suffix) | Low | rename; a rule at `warning` severity would have failed the build |
| Misleading names | `GetX` that mutates, `IsX` returning non-bool, `Manager`/`Helper`/`Data`/`Info` nouns | Low | name the behaviour |
| Abbreviations and Hungarian | `strName`, `lstItems`, `tmp`, `cnt` | Low | full words |
| Inconsistent suffixes | `OrderVm` beside `CustomerViewModel`; `FooSvc` beside `BarService` | Low | one suffix per role |

## Suppressions and warnings

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Suppression without justification | `#pragma warning disable`, `[SuppressMessage]` with no `Justification`, `<NoWarn>` in a csproj | Medium | fix the warning; keep a suppression only with a reason and the narrowest scope |
| Null-forgiving to silence | `x!` where `x` can be null; `= null!` on members never initialised | Medium | a real initialisation, a `required` member, or a nullable type |
| `TreatWarningsAsErrors` off locally | `<TreatWarningsAsErrors>false</TreatWarningsAsErrors>` in a project | High | remove; fix the warnings (dotnet-solution-config) |
| Build properties repeated per project | `LangVersion`/`Nullable`/`ImplicitUsings`/`TreatWarningsAsErrors` in a csproj | Low | `Directory.Build.props` only (dotnet-solution-setup) |

## Dead and stale code

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Commented-out code | blocks of `//` code, `/* … */` around statements | Low | delete; git remembers |
| Unused members | private members never referenced (IDE0051/IDE0052), unused parameters (IDE0060), unused usings (IDE0005) | Low | delete |
| Unreachable branches | `if (false)`, code after `return`, a `#if DEBUG` block carrying production logic | Low | delete, or move the logic out of the conditional |
| `TODO` without owner or context | `// TODO` / `// FIXME` / `// HACK` with no who, what or issue reference | Low | add the owner and the intent, or do it |
| Obsolete members kept | `[Obsolete]` members with no removal plan, or with new callers | Low | remove, or document the deprecation window |

## Usings and files

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Implicit usings enabled | `<ImplicitUsings>enable</ImplicitUsings>` anywhere | Medium | `disable`; every file declares its usings (dotnet-solution-setup) |
| Global usings as a shortcut | a `GlobalUsings.cs` re-creating the implicit set | Low | explicit usings per file |
| Namespace style mixed | file-scoped `namespace X;` and block-scoped in the same project | Low | the `.editorconfig` setting, consistently |
| Oversized files | a file over ~500 lines; several top-level types per file | Low | one type per file; split by responsibility (`solid.md`) |
| Regions | `#region` used to hide length | Low | split the class |

## Formatting

Never a finding on its own: `dotnet format --verify-no-changes` is the check, and a non-empty output is one Low finding ("formatting drift in N files"). Line endings are never a finding.
