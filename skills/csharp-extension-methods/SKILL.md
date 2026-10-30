---
name: csharp-extension-methods
description: Use when adding helper, utility, or convenience members that operate on a type — especially on framework or third-party types — or when writing any C# extension method.
metadata:
  version: "1.0.1"
---

# Extension methods — C# 14 extension blocks

When functionality operates on a type but isn't part of its core responsibility, use an extension method rather than adding it to the class. Especially for: operations on framework/third-party types, cross-cutting helpers (formatting, mapping, validation, LINQ-style chains), and functionality that would bloat the source type.

Group related extensions in `<Type>Extensions` static classes (`StringExtensions`, `EnumerableExtensions`, …) in a namespace close to the consumers, not the source type. Keep them stateless and side-effect free where possible.

**Use C# 14 extension blocks, not the legacy `this`-parameter syntax** (legacy form only when the project's language version is below 14):

```csharp
using System.Collections.Generic;
using System.Linq;

public static class EnumerableExtensions
{
    extension<TSource>(IEnumerable<TSource> source)
    {
        public bool IsEmpty => !source.Any();

        public IEnumerable<TSource> WhereNotNull()
            => source.Where(item => item is not null);
    }
}
```

One `extension(...)` block per receiver type/shape inside the static class, grouping related members together.

## Verified C# 14 syntax rules

- Named receiver (`extension(string value)`) → **instance** extension members; unnamed receiver (`extension(string)`) → **static** extension members only.
- Generic receivers take constraints after the parens: `extension<T>(IEnumerable<T> source) where T : class { … }`.
- Blocks may contain methods, **properties**, and operators (no conversion operators). Not allowed: fields/instance state, constructors, indexers, events, auto-properties.
- Multiple blocks per static class are fine; classic `this`-methods and blocks coexist (identical IL — converting legacy → block is binary-compatible). All members across the class need unique signatures.
- Compiler-only feature: works on `netstandard2.0` with `<LangVersion>14</LangVersion>` (note: officially Microsoft calls LangVersion-above-TFM unsupported — the house convention accepts this; see dotnet-solution-setup).

## What stays on the class

Members that touch private state, are part of the type's identity/invariants, or must be polymorphic belong on the class itself — don't force them into extensions.

## Common mistakes

| Mistake | Fix |
|---|---|
| `public static bool IsEmpty<T>(this IEnumerable<T> source)` in new C# 14 code | Extension block with a named receiver |
| Extensions namespaced next to the source type | Namespace close to the consumers |
| One giant `Extensions` class for everything | One `<Type>Extensions` class per receiver type |
| Stateful extension class (caches, counters) | Make it a DI service instead (see dotnet-di-design) |

Every file declares its own `using` directives — no implicit usings (see dotnet-solution-setup).

If an existing codebase consistently uses legacy `this` syntax, match it and flag the divergence rather than mixing both forms in one project.
