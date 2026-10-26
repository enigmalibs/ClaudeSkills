# Your own icons — `SvgIconSet` and custom `IIconSet`s

Phosphor has no privileged route through this library. The `Icon` control's
`IconSet`/`IconName`/`Variant` path and all three extension methods take **any** `IIconSet`, so a glyph
parsed from your own `.svg` renders exactly like a built-in one.

Two ways in: `SvgIconSet` over your artwork (almost always the answer), or your own `IIconSet`
implementation (when the icons come from somewhere `SvgIconSet` cannot read).

## `SvgIconSet` — four factories

`Enigma.Icons.SvgIconSet` is a `sealed class : IIconSet`. There is no public constructor.

```csharp
using System.Collections.Generic;
using System.Reflection;
using Enigma.Icons;

// A directory tree. Subfolders are variants by default.
public static SvgIconSet FromDirectory(
    string path,
    bool variantsFromSubfolders = true,
    string? defaultVariant = null,
    string? name = null);

// Embedded resources in an assembly, matched by ordinal prefix.
public static SvgIconSet FromAssembly(
    Assembly assembly,
    string resourcePrefix,
    string? defaultVariant = null,
    string? name = null);

// An explicit file list. No variants.
public static SvgIconSet FromFiles(
    IEnumerable<string> files,
    string? name = null);

// Name → SVG text pairs. No variants. The in-memory escape hatch.
public static SvgIconSet FromSvgSources(
    IEnumerable<KeyValuePair<string, string>> sources,
    string? name = null);
```

**Build the set once** — at startup, or as a static/singleton ViewModel property — and bind it. Do not
construct one per view: discovery is eager and the glyph cache lives on the instance.

### `FromDirectory`

```
Assets/Icons/
├── regular/  logo.svg  chart.svg
└── bold/     logo-bold.svg  chart-bold.svg
```

```csharp
using Enigma.Icons;

IIconSet mine = SvgIconSet.FromDirectory("Assets/Icons", name: "House");
```

```xml
<ei:Icon IconSet="{Binding MyIconSet}" IconName="logo" Variant="bold" Size="32" />
```

- Each immediate subdirectory is a variant; its `.svg` files are its icons. Pass
  `variantsFromSubfolders: false` for a flat folder — the set then has **no** variants, and passing
  `defaultVariant` alongside it throws `ArgumentException`.
- A file name ending `-<variant>` has that suffix stripped, so `bold/logo-bold.svg` and `bold/logo.svg`
  both yield icon `logo` in variant `bold`. That is what makes an extracted Phosphor tree work unchanged.
- `defaultVariant` omitted → `regular` if it was discovered, else the first variant in ordinal order.
- `name` omitted → the directory's leaf name. It only shows up in exception messages.
- Two files in one variant that normalize to the same name collide; the first in ordinal file-name order
  wins, silently.
- Throws `ArgumentNullException` (null path), `DirectoryNotFoundException` (missing directory), and
  `ArgumentException` in three distinct cases: `defaultVariant` supplied with `variantsFromSubfolders:
  false`; `defaultVariant` supplied when the root has **no subdirectories at all** ("no variants were
  discovered"); and `defaultVariant` not among the discovered variants.

**Path safety, deliberately strict.** Enumeration is **top-directory only** — never recursive. Symlinked
variant subdirectories *and* symlinked `.svg` files are skipped, and every path actually read is
constrained to the root, so no entry can point the set at content outside it. A skipped entry is dropped
**silently**, so one hostile entry cannot deny service on an otherwise valid directory. The flip side: a
symlinked icon you *meant* to include just quietly is not there.

Two deployment details the library's own docs never cover, and both bite on the first run:

**1. The path resolves against the working directory, not the executable.** `FromDirectory` does
`Path.GetFullPath(path)`, so a relative `"Assets/Icons"` breaks for a published app started from elsewhere,
for a macOS `.app` bundle, and under most IDE debug configurations. Always anchor it:

```csharp
using System;
using System.IO;
using Enigma.Icons;

IIconSet mine = SvgIconSet.FromDirectory(
    Path.Combine(AppContext.BaseDirectory, "Assets", "Icons"));
```

**2. The files must actually be copied to the output.** `FromDirectory` reads the real filesystem:

```xml
<ItemGroup>
  <Content Include="Assets\Icons\**\*.svg" CopyToOutputDirectory="PreserveNewest" />
</ItemGroup>
```

### `FromAssembly` — deployment-safe, but mind the build action

Embedding avoids the working-directory and copy-to-output problems entirely. The catch: `FromAssembly` reads
**manifest** resources, and the Avalonia app template puts assets under `<AvaloniaResource>`, which are
packed into Avalonia's own `avares` blob and are **not** manifest resources. That combination throws
`ArgumentException` ("No embedded resource … starts with …") on the most likely first attempt.

Use `EmbeddedResource` for icons you feed to `FromAssembly`:

```xml
<ItemGroup>
  <EmbeddedResource Include="Assets\Icons\**\*.svg" />
</ItemGroup>
```

```csharp
using Enigma.Icons;

IIconSet mine = SvgIconSet.FromAssembly(
    typeof(App).Assembly,
    "MyApp.Assets.Icons.",
    name: "House");
```

Manifest resource names are dot-flattened. After the prefix and the `.svg` suffix are removed, the
**last** dot-separated segment is the icon name and the segment before it, if any, is the variant;
anything further left is ignored. A `-<variant>` filename suffix is stripped here too, so
`MyApp.Icons.bold.acorn-bold.svg` indexes as icon `acorn` in variant `bold`. Keep the layout uniform —
resources with a variant segment and resources without get grouped inconsistently, and the ones without land
in a nameless variant that is not listed in `Variants`.

Getting the prefix right is guesswork until you look, so print the real names once:

```csharp
using System;

foreach (string n in typeof(App).Assembly.GetManifestResourceNames())
{
    Console.WriteLine(n);
}
```

**If you must keep `AvaloniaResource`**, there is no `FromAvaloniaResource` factory — read the asset
yourself and parse it:

```csharp
using System;
using System.IO;
using Avalonia.Platform;
using Enigma.Icons;

using Stream s = AssetLoader.Open(new Uri("avares://MyApp/Assets/logo.svg"));
IconGlyph glyph = SvgIconParser.Parse(s);      // or collect pairs and use FromSvgSources
```

### `FromFiles` and `FromSvgSources`

`FromFiles` takes explicit paths, has no variants, and validates **eagerly** — a listed file that does not
exist throws `FileNotFoundException` at construction, not at first lookup. `FromSvgSources` takes the SVG
text directly, which is ideal for tests and for generated artwork:

```csharp
using System.Collections.Generic;
using Enigma.Icons;

IIconSet shapes = SvgIconSet.FromSvgSources(
[
    new KeyValuePair<string, string>("logo",
        """
        <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/></svg>
        """),
]);
```

## The SVG subset the parser accepts

`SvgIconParser` (used by every `SvgIconSet`) is a static class:

```csharp
using System.IO;

namespace Enigma.Icons;

public static class SvgIconParser
{
    public static int MaxDocumentBytes { get; set; }   // default 1 MiB; process-wide
    public static IconGlyph Parse(string svg);
    public static IconGlyph Parse(Stream stream);
}
```

| Supported | Details |
|---|---|
| Elements | `svg`, `g`, `path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon` |
| Transforms | `matrix`, `translate`, `scale`, `rotate`, `skewX`, `skewY` — **baked into the path data** |
| Paint | `fill`, `stroke`, `stroke-width`, `stroke-linecap`, `stroke-linejoin`, `fill-rule`, `opacity` |
| Also | inline `style="…"`, group inheritance, `viewBox`, `currentColor` (normalized to `null`) |

**Not supported:** `<use>`, `<defs>`, `<text>`, `<clipPath>`, `<mask>`, gradients, patterns, filters,
CSS `<style>` blocks, animation, embedded raster images. Unsupported elements are ignored; if nothing
paintable is left, `Parse` throws `SvgParseException`. Convert text to paths and flatten `<use>` before
shipping artwork through this parser.

Every non-`path` shape is converted to path data, so `IconLayer.PathData` is always the SVG path
mini-language and a layer never carries a transform.

**Security posture:** `DtdProcessing.Prohibit` and `XmlResolver = null`, so XXE and external-entity
expansion are closed outright, and a document larger than `MaxDocumentBytes` is rejected *before* parsing.

`MaxDocumentBytes` is **process-wide static mutable state**, not a per-parse option — a library that lowers
it changes it for the whole host app. Restore it if you touch it.

`Parse(Stream)` does **not** dispose the stream you hand it (it copies into an internal buffer), and it stops
reading at `MaxDocumentBytes + 1`, so an over-limit stream is left positioned mid-document. Own the
disposal yourself with `using`.

### Caching, and why edits do not show up

`SvgIconSet` caches every resolved glyph and has **no public invalidation** — no `Clear`, `Reset` or
`Dispose`. Editing an `.svg` on disk after the icon has been resolved once changes nothing at runtime. To
pick up edits you must build a **new** `SvgIconSet` *and reassign* `Icon.IconSet`: mutating or replacing the
set's contents re-renders nothing, because only a property change triggers `AffectsRender`.

One nuance in the other direction: a **faulted** parse is evicted rather than cached, so a transient I/O
failure does not poison the entry — it is retried on the next lookup. The "cached, reference-equal"
guarantee therefore holds for successful parses only.

## Implementing `IIconSet` yourself

```csharp
using System.Collections.Generic;

namespace Enigma.Icons;

public interface IIconSet
{
    string Name { get; }                       // used in exception messages, e.g. "Phosphor"
    IReadOnlyList<string> Variants { get; }     // lower-case; empty for a single-style set
    string? DefaultVariant { get; }             // null when the set has no variants
    IEnumerable<string> IconNames { get; }      // lower-case kebab-case, ordered
    bool TryGetGlyph(string icon, string? variant, out IconGlyph? glyph);
    IconGlyph GetGlyph(string icon, string? variant = null);
}
```

There are **no default interface members** (`netstandard2.0` is in the TFM set), so you implement both
lookups — and you must repeat the `variant = null` default argument, or callers holding a class-typed
reference lose it.

The contract every implementation must honour:

1. **Name lookup is case-insensitive** and accepts kebab-case, `snake_case` or PascalCase, normalized
   internally to kebab-case. Same for variants.
2. **`variant == null` means `DefaultVariant`.** A variant the set does not have is a **miss, never a
   silent fallback** — a caller asking for `bold` must not get `regular` back.
3. **Repeated calls for the same `(icon, variant)` return a cached, reference-equal `IconGlyph`.**
   Not optional: the Avalonia geometry cache is keyed on the glyph *instance*, so a fresh object per call
   silently costs a `Geometry.Parse` on every render pass of every icon.
4. **Every member is safe for concurrent use from any thread.** The control calls you from the UI thread's
   render pass; a data-loading path may call you from another.
5. **A null `icon` is a miss for `TryGetGlyph`** (return `false`, do not throw) and
   **`ArgumentNullException` for `GetGlyph`**. The null guard sits ahead of name normalization.
6. **`Try` governs absence, not corruption.** A miss → `false` / `IconNotFoundException`. A source that is
   *present but broken* — malformed SVG, an unreadable or vanished file, a corrupt resource — **throws from
   both**, as `SvgParseException` or `InvalidDataException`. Silently reporting a broken source as "not
   found" turns a fixable bug into an invisible blank space.
   For reference, the in-box `SvgIconSet` wraps `IOException` and `UnauthorizedAccessException` from a
   lookup in `SvgParseException`; raw I/O exceptions escape only from the **factories**
   (`DirectoryNotFoundException`, `FileNotFoundException`), never from `TryGetGlyph`/`GetGlyph`.

```csharp
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using Enigma.Icons;

/// <summary>A single-style set over SVG text keyed by name — e.g. rows fetched from a database.</summary>
public sealed class MyIconSet : IIconSet
{
    // Ordinal: the keys are already canonical kebab-case.
    private readonly IReadOnlyDictionary<string, string> _svgByName;
    private readonly ConcurrentDictionary<string, IconGlyph> _cache =
        new ConcurrentDictionary<string, IconGlyph>(StringComparer.Ordinal);

    public MyIconSet(IReadOnlyDictionary<string, string> svgByName)
        => _svgByName = svgByName ?? throw new ArgumentNullException(nameof(svgByName));

    public string Name => "MyIcons";
    public IReadOnlyList<string> Variants => Array.Empty<string>();
    public string? DefaultVariant => null;
    public IEnumerable<string> IconNames => _svgByName.Keys.OrderBy(k => k, StringComparer.Ordinal);

    public bool TryGetGlyph(string icon, string? variant, out IconGlyph? glyph)
    {
        glyph = null;

        // Null icon is a miss, not a throw. This set has no variants, so any variant is a miss too.
        if (icon is null || variant is not null)
        {
            return false;
        }

        string key = icon.Trim().Replace('_', '-').ToLowerInvariant();
        if (!_svgByName.TryGetValue(key, out string? svg))
        {
            return false;
        }

        // GetOrAdd, so repeated calls are reference-equal — the geometry cache depends on it.
        // A parse failure propagates, by design: corruption is not absence.
        glyph = _cache.GetOrAdd(key, _ => SvgIconParser.Parse(svg));
        return true;
    }

    public IconGlyph GetGlyph(string icon, string? variant = null)
    {
        if (icon is null)
        {
            throw new ArgumentNullException(nameof(icon));
        }

        return TryGetGlyph(icon, variant, out IconGlyph? glyph) && glyph is not null
            ? glyph
            : throw new IconNotFoundException(icon, variant, Name);
    }
}
```

That `Replace('_', '-').ToLowerInvariant()` is a simplification — it does not split PascalCase the way the
built-in normalizer does. Wrap `SvgIconSet` if you want the full equivalence classes.

Prefer wrapping `SvgIconSet` over reimplementing this. Write your own only when the artwork comes from a
place `SvgIconSet` cannot reach — a database, an HTTP cache, a font, a generated shape.

## Exposing the set to XAML

The control needs an `IIconSet` *instance*, so it comes from the DataContext:

```csharp
using Enigma.Icons;

public sealed class MainWindowViewModel
{
    private static readonly IIconSet Shapes = SvgIconSet.FromDirectory("Assets/Icons");

    public IIconSet MyIconSet => Shapes;
}
```

```xml
<ei:Icon IconSet="{Binding MyIconSet}" IconName="logo" Variant="bold" Size="32" />
```

There is **no** markup extension for custom sets, and no `IconSet` on `{ei:IconGeometry}` /
`{ei:IconImage}` — those two are Phosphor-typed. From code, use the extension methods directly:

```csharp
using Avalonia.Media;
using Enigma.Icons.Avalonia;

Geometry g = mine.GetGlyph("logo", "bold").ToGeometry();
```

To name `SvgIconSet` or `IIconSet` **in XAML** — for an `x:Static` reference or direct construction — you
need a second prefix: the `ei` URI maps only `Enigma.Icons.Avalonia` and `…Avalonia.Markup`, not
`Enigma.Icons`.

```xml
xmlns:eic="using:Enigma.Icons"
```

**There is no ambient default set.** `IconSetProperty` is a plain non-inheriting `StyledProperty` with a
`null` default — there is no attached form and no app-wide "default icon set", so every `Icon` needs it. The
scalable answer is a style setter:

```xml
<Style Selector="ei|Icon.house">
  <Setter Property="IconSet" Value="{x:Static my:AppIcons.Set}" />
</Style>
```

Scope it to a class, as above. A broad `Selector="ei|Icon"` setter would blank **every** `Kind`-based icon in
scope, because a non-null `IconSet` wins unconditionally and the setter supplies no `IconName`.

**Debugging a custom set.** `Icon.Render` swallows everything and never logs, so the control gives you no
feedback at all. Call the set directly:

```csharp
using Avalonia.Media;
using Enigma.Icons;
using Enigma.Icons.Avalonia;

IconGlyph glyph = mine.GetGlyph("logo", "bold");   // throws IconNotFoundException / SvgParseException
Geometry g = glyph.ToGeometry();                   // throws on malformed path data
```

## Common mistakes

- **Building the set per view or per binding evaluation** → re-discovery and a cold glyph cache each time,
  which also defeats the geometry cache. Build it once.
- **Returning a fresh `IconGlyph` per call from a custom set** → a `Geometry.Parse` on every render pass.
  Cache and return reference-equal instances.
- **Falling back to the default variant on an unknown one** → violates the contract; a caller asking for
  `bold` must not get `regular`.
- **Swallowing parse failures in `TryGetGlyph`** → also a contract violation. Only *misses* return
  `false`.
- **`FromDirectory` on a flat folder with the default `variantsFromSubfolders: true`** → zero icons and no
  exception. Pass `false`.
- **Passing `defaultVariant` with `variantsFromSubfolders: false`** → `ArgumentException`.
- **Expecting recursion or symlink following** → neither happens; both are silently skipped.
- **Forgetting `CopyToOutputDirectory`** → `DirectoryNotFoundException` (or an empty set) in the published
  app only. Prefer `FromAssembly` with `EmbeddedResource`.
- **A relative path in `FromDirectory`** → resolved against the **working directory**, which a desktop app
  must not depend on. Use `Path.Combine(AppContext.BaseDirectory, …)`.
- **`FromAssembly` over `<AvaloniaResource>` assets** → `ArgumentException`: those live in the `avares` blob,
  not in manifest resources. Switch the build action to `EmbeddedResource`, or read them with
  `AssetLoader.Open`.
- **Guessing the manifest resource prefix** → print `GetManifestResourceNames()` once instead.
- **Artwork using `<use>`, `<text>` or gradients** → ignored, and possibly `SvgParseException` for "no
  paintable element". Flatten before shipping.
- **Expecting an edited `.svg` to appear on reload** → the set caches forever. Build a new set *and* reassign
  `Icon.IconSet`.
- **Expecting an app-wide default `IconSet`** → there is none; use a class-scoped style setter.
