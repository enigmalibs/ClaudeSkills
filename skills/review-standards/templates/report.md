# Code review — <scope> — <yyyy-mm-dd>

Written by `/review` v1 with `review-standards` v1. Read-only: nothing in the repository was changed.

## Scope & method

- **Solution:** `<path/to/Solution.slnx>` (<N> projects) at `<branch> @ <short sha>`.
- **Scope:** <full solution | work items `<ID>`, `<ID>` — commits `<sha>`, `<sha>` (<N> files) | path `<path>`>.
- **Dimensions:** <all ten | `SOLID`, `XAML`, … (restricted by the argument text)>.
- **Rulebook:** <dotnet-di-design, dotnet-async, communitytoolkit-mvvm, avalonia v2, enigma-avalonia-desktop v3, xunit-v3 v6, csharp-extension-methods> + `review-standards` v1 references <solid, xaml, …>.
- **Mode:** <inline | sub-agents per dimension, merged and de-duplicated>.

## Baseline

| Step | Result |
|---|---|
| `dotnet build <Solution.slnx>` | <0 errors, 12 warnings — CA2254 ×7, AVLN2100 ×3, IDE0005 ×2 \| not completed: <reason>> |
| `dotnet test --solution <Solution.slnx>` | <passed 184 · failed 0 · skipped 2 \| no tests \| not completed: <reason>> |

<One line on what the baseline implies, e.g. "The three AVLN2100 warnings are XAML-01 below.">

## Summary

| Severity | Findings | Locations |
|---|---|---|
| Critical | <n> | <n> |
| High | <n> | <n> |
| Medium | <n> | <n> |
| Low | <n> | <n> |
| **Total** | **<n>** | **<n>** |

<Three lines: the one thing to fix first, the dominant pattern, the overall state.>

## Plan conformance

<Work-item scope only — delete this section otherwise. One block per item:>

### <FEATURE-3A7F> — <title>

| Criterion | Status | Evidence |
|---|---|---|
| 1. <criterion text from docs/plan/<ID>.md> | <met \| partial \| not met \| not verifiable> | <`path:line`, a commit, or why it is not verifiable> |

**Outside the plan** — <files or behaviour added without a criterion, or "none">.
**Done doc vs diff** — <claims in docs/done/<ID>*.md not backed by the diff, or "consistent">.

## Findings

<Severity order, Critical first; within a severity, dimension order SOLID · XAML · LOG · EXC · ASYNC · MVVM · TEST · SEC · STYLE · PERF · PLAN. One finding per pattern, every location listed. The shape is mandatory (review-standards *Finding shape*):>

### <EXC-03> — [<High>] <Empty catch blocks swallow I/O errors on the save path>

**Locations**
- `<src/App/Services/FileSync.cs:88>`
- `<src/App/Services/FileSync.cs:142>`

**Why it matters** — <the consequence, not the rule>.

**Recommended fix** — <one concrete change that closes every location>.

**Rule** — <review-standards `reference/exceptions.md` §Catch blocks; dotnet-async *CancellationToken*>.

## In good shape

- <Three to six lines: what the next dev should keep doing, one `path` each.>

## Hand-off

Plan the fixes as a `CODE-REVIEW` item — one phase per finding you keep:

```
/interview @docs/review/<yyyy-mm-dd>-<scope>.md
```

Or plan and build it unattended:

```
/vibe @docs/review/<yyyy-mm-dd>-<scope>.md
```

Then `/build <CODE-REVIEW-ID>` (one phase at a time) or `/bulk` (every phase). This report is read-only input: nothing changes until one of those runs.
