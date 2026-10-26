# The C# API

Everything you need from code: converting a glyph to Avalonia primitives, looking icons up in the
Phosphor set, and the model types the whole library is built on. The four namespaces, at a glance (every
snippet below still carries its own using lines; an API listing carries its type's own `namespace`):

```csharp
using Avalonia.Media;
using Enigma.Icons;                  // IIconSet, IconGlyph, IconLayer, IconViewBox, exceptions
using Enigma.Icons.Avalonia;         // IconGlyphExtensions
using Enigma.Icons.Phosphor;         // PhosphorIconSet, PhosphorIcon, PhosphorWeight, PhosphorIconNames
```

## `IconGlyphExtensions` — glyph → Avalonia

```csharp
using Avalonia.Media;
using Enigma.Icons;

namespace Enigma.Icons.Avalonia;

public static class IconGlyphExtensions
{
    public static Geometry     ToGeometry(this IconGlyph glyph);
    public static Drawing      ToDrawing(this IconGlyph glyph, IBrush brush);
    public static DrawingImage ToDrawingImage(this IconGlyph glyph, IBrush brush);
}
```

They take an `IconGlyph` from **any** `IIconSet` — nothing here is Phosphor-specific, and a glyph parsed
from your own `.svg` renders exactly like a built-in one. All three throw `ArgumentNullException` on a
null argument.

| Method | Returns | Per-layer opacity | Use for |
|---|---|---|---|
| `ToGeometry` | `Geometry` | **lost** | `Path.Data`, clip geometry, any `Geometry?` slot |
| `ToDrawing` | `Drawing` (a `DrawingGroup`) | preserved | `DrawingPresenter`, composing drawings |
| `ToDrawingImage` | `DrawingImage` | preserved | `Image.Source`, any `IImage?` slot |

- **`ToGeometry`**: a one-layer glyph becomes the parsed path itself; a multi-layer glyph becomes a
  `GeometryGroup` whose children are the layers in paint order, with `FillRule` taken from the **first**
  layer. Since a `GeometryGroup` has no per-child opacity and one shared fill rule, a `Duotone` glyph
  collapsed this way paints its 20 % backing shape solid. Deliberately allowed — `Path.Data` needs a
  single `Geometry` — but wrong for duotone.
  It branches on `Layers.Count == 1`, **not** on `IsSingleLayer`, so a *one-layer* glyph that is stroked or
  translucent also collapses to a bare parsed path and loses its stroke metadata and opacity silently.
  `IconLayer.FillRule` is read in exactly one place — the multi-layer `GeometryGroup` — so on every other
  path (a one-layer glyph, `ToDrawing`, the control) an `evenodd` rule from your SVG is **dropped** and the
  renderer's default rule applies.
- **`ToDrawing`**: a root `DrawingGroup` holding one `GeometryDrawing` per *painted* layer, in order. A
  layer with `Opacity < 1` is wrapped in its own `DrawingGroup` carrying that opacity (a
  `GeometryDrawing` has none). A layer that is neither filled nor stroked contributes nothing at all.
- **Fill/stroke rules are identical to the control's** (`icon-control.md`): `brush` always wins for
  fills; a layer's own parseable `stroke` colour wins for strokes; an unparseable one falls back to
  `brush` silently.

**Unlike the control, these propagate exceptions.** A `Geometry.Parse` failure on malformed path data is
allowed to escape — malformed data in a committed asset is a bug, not a runtime condition.

**Every call parses afresh, and the result is yours.** A `Geometry` is mutable (its `Transform` is
settable), so a shared instance would let one caller's change reach every other. Two calls for the same
glyph return independent objects — which is also what putting one in a `GeometryGroup` and another in a
`Path.Data` requires. (The `Icon` control caches internally *because* it never hands its geometry out.)
If you convert the same glyph on a hot path, cache the result yourself: `Geometry.Parse` costs ~34 µs.

### All three drop the view box

Every Phosphor glyph is authored in `0 0 256 256`, and only the `Icon` control maps that box. A `Geometry`
carries no view box, and `ToDrawingImage` never sets `DrawingImage.Viewbox` — so both report the glyph's
**tight ink bounds**:

| Icon (`Regular`) | `glyph.ViewBox` | `DrawingImage.Size` / `ToGeometry().Bounds` |
|---|---|---|
| `Acorn` | 0 0 256 256 | 208 × 232 |
| `Minus` | 0 0 256 256 | **184 × 16** |
| `DotOutline` | 0 0 256 256 | **32 × 48** |

So an `Image` at 24 × 24 fed a `Minus` renders a 24 × 2 sliver, and a set of icons sized this way shares no
optical grid. Restore it explicitly — there is no library API and no overload that does it for you:

```csharp
using Avalonia;
using Avalonia.Media;
using Enigma.Icons.Avalonia;

DrawingImage img = glyph.ToDrawingImage(Brushes.Black);
img.Viewbox = new Rect(0, 0, 256, 256);      // Rect? — Size becomes 256 × 256
```

For a `Geometry` there is no equivalent fix; give the `Path` a fixed `Width`/`Height`, or use the control.

```csharp
using Avalonia.Controls;
using Avalonia.Controls.Shapes;
using Avalonia.Media;
using Enigma.Icons.Avalonia;
using Enigma.Icons.Phosphor;

Geometry geometry = PhosphorIconSet.Instance
    .GetGlyph(PhosphorIcon.Acorn, PhosphorWeight.Bold)
    .ToGeometry();

var path = new Path { Data = geometry, Fill = Brushes.Black, Stretch = Stretch.Uniform };

var image = new Image
{
    Source = PhosphorIconSet.Instance
        .GetGlyph(PhosphorIcon.Heart, PhosphorWeight.Duotone)
        .ToDrawingImage(Brushes.Crimson),          // duotone-correct
    Width = 24,
    Height = 24,
};
```

## `PhosphorIconSet` — the artwork

```csharp
using System.Collections.Generic;
using Enigma.Icons;

namespace Enigma.Icons.Phosphor;

public sealed class PhosphorIconSet : IIconSet
{
    public static PhosphorIconSet Instance { get; }        // no public constructor

    public string Name { get; }                            // always "Phosphor"
    public IReadOnlyList<string> Variants { get; }          // thin, light, regular, bold, fill, duotone
    public string? DefaultVariant { get; }                  // "regular"
    public IEnumerable<string> IconNames { get; }           // all 1,512, no resource read

    // The typed surface — the ergonomic path
    public IconGlyph GetGlyph(PhosphorIcon icon, PhosphorWeight weight = PhosphorWeight.Regular);
    public bool TryGetGlyph(PhosphorIcon icon, PhosphorWeight weight, out IconGlyph? glyph);

    // The IIconSet surface — makes it interchangeable with any other set
    public IconGlyph GetGlyph(string icon, string? variant = null);
    public bool TryGetGlyph(string icon, string? variant, out IconGlyph? glyph);
}
```

1,512 icons × 6 weights, served from six embedded `.dat` resources holding **path data, not SVG** — the
SVG parser is not on this code path at all.

- **Nothing is read at construction.** Touching `Instance` costs nothing. A weight's table is loaded on
  first use of *that weight* and kept for the process's life; every resolved `IconGlyph` is cached, so
  repeated lookups return the **same instance**.
- **Thread-safe on every member** — both caches are `ConcurrentDictionary`, the model is immutable.
- Note `TryGetGlyph(PhosphorIcon, …)` has **no default** for `weight`, while `GetGlyph` defaults it to
  `Regular`.

Exceptions — and note what `Try` does *not* swallow:

| Condition | `GetGlyph` | `TryGetGlyph` |
|---|---|---|
| Icon/variant not in the set (a **miss**) | `IconNotFoundException` | `false` |
| Undefined enum value (a cast integer) | `ArgumentOutOfRangeException` | **throws too** |
| Missing or corrupt embedded resource | `InvalidDataException` | **throws too** |
| `null` name (string overload) | `ArgumentNullException` | `false` |

`Try` governs *absence*, not *corruption*: silently reporting a broken resource as "icon not found" would
turn a fixable packaging bug into an invisible blank space.

## `PhosphorWeight`

```csharp
namespace Enigma.Icons.Phosphor;

public enum PhosphorWeight { Thin, Light, Regular, Bold, Fill, Duotone }
```

- **`default(PhosphorWeight)` is `Thin`, not `Regular`.** Every API in the package defaults a weight to
  `Regular` *explicitly*; the trap is your own code writing `default`, `new PhosphorWeight()`, or an
  uninitialised field. It fails silently, as thin artwork.
- **`Duotone` is two layers** — a tinted backing shape at 20 % opacity behind the foreground shape. Use
  the control, `ToDrawing` or `ToDrawingImage`; `ToGeometry` flattens the opacity away.
- The declaration order is load-bearing (it indexes the resource-name table). Never reorder it.

## `PhosphorIcon` and `PhosphorIconNames`

`PhosphorIcon` is a generated enum with **1,512** members in PascalCase, ordinal-ordered:
`Acorn`, `AddressBook`, `AddressBookTabs`, `AirTrafficControl`, `Airplane`, `AirplaneInFlight`, …,
`NumberCircleEight`, `ListNumbers`, …

**Never call `Enum.ToString()`, `Enum.GetName` or `Enum.Parse` on it.** Use the generated tables — they
are the trimming-safe path (a table lookup survives trimming; reflection over enum metadata does not) and
avoid reflection over 1,512 members:

```csharp
using System.Collections.Generic;

namespace Enigma.Icons.Phosphor;

public static class PhosphorIconNames
{
    public static IReadOnlyList<string> All { get; }               // kebab-case, in enum order
    public static string ToKebabCase(PhosphorIcon icon);           // PhosphorIcon.AddressBook -> "address-book"
    public static bool TryParse(string name, out PhosphorIcon icon);
}
```

`All` is guaranteed to be in **enum order**, so the index *is* the `PhosphorIcon` value — which is how you
build a searchable catalogue with no parsing at all:

```csharp
using System.Collections.Generic;
using Enigma.Icons.Phosphor;

public sealed record IconEntry(PhosphorIcon Kind, string Name);   // your own item type

IReadOnlyList<string> names = PhosphorIconNames.All;
var catalog = new IconEntry[names.Count];
for (int i = 0; i < catalog.Length; i++)
{
    catalog[i] = new IconEntry((PhosphorIcon)i, names[i]);   // no Enum.Parse, no reflection
}
```

`TryParse` accepts kebab-case, `snake_case` or PascalCase, case-insensitively, and treats `null`/empty as
a miss rather than throwing.

## The model types (`Enigma.Icons`)

All immutable and thread-safe.

```csharp
using System.Collections.Generic;

namespace Enigma.Icons;

public sealed class IconGlyph
{
    public IconGlyph(IconViewBox viewBox, IReadOnlyList<IconLayer> layers);
    public IconViewBox ViewBox { get; }
    public IReadOnlyList<IconLayer> Layers { get; }   // paint order, index 0 first/bottom; never empty
    public bool IsSingleLayer { get; }                // 1 layer, opacity >= 1, not stroked
}
```

The constructor copies `layers` defensively into a read-only snapshot; it throws `ArgumentNullException`
for a null list and `ArgumentException` for an empty list or a null element.

```csharp
namespace Enigma.Icons;

public sealed class IconLayer
{
    public IconLayer(
        string pathData,                              // SVG path mini-language; not null/empty/whitespace
        double opacity = 1.0,                         // 0.0–1.0 inclusive; NaN rejected
        IconFillRule fillRule = IconFillRule.NonZero,
        string? fill = null,                          // null = inherit the renderer's brush
        string? stroke = null,
        double? strokeWidth = null,
        IconLineCap? strokeLineCap = null,
        IconLineJoin? strokeLineJoin = null);

    public string PathData { get; }
    public double Opacity { get; }
    public IconFillRule FillRule { get; }
    public string? Fill { get; }
    public string? Stroke { get; }
    public double? StrokeWidth { get; }
    public IconLineCap? StrokeLineCap { get; }
    public IconLineJoin? StrokeLineJoin { get; }
    public bool IsStroked { get; }        // Stroke is non-null and not "none"
    public bool IsFilled { get; }         // Fill is anything except the literal "none"
}

public enum IconFillRule { NonZero, EvenOdd }
public enum IconLineCap  { Flat, Round, Square }     // Flat == SVG "butt"
public enum IconLineJoin { Miter, Round, Bevel }
```

`Fill` and `Stroke` are **raw SVG paint strings, not a colour type** — `Enigma.Icons` has zero
dependencies and therefore no framework colour type. `null` is the normalized form of `"currentColor"`
and is what makes "inherit the renderer's brush" the default. A `null` `Fill` **is filled**; only the
literal `"none"` disables filling. A layer never carries a transform — the parser bakes every SVG
transform into `PathData`.

```csharp
using System;

namespace Enigma.Icons;

public readonly struct IconViewBox : IEquatable<IconViewBox>
{
    public IconViewBox(double x, double y, double width, double height);   // width/height must be > 0
    public double X { get; }
    public double Y { get; }
    public double Width { get; }
    public double Height { get; }
    public static IconViewBox Default { get; }        // 0 0 256 256 — every Phosphor icon
    // Equals / GetHashCode / ToString / == / != are all implemented
}
```

`ToString()` returns `"X Y Width Height"` in the invariant culture. A non-positive or `NaN` width/height
throws `ArgumentOutOfRangeException`.

**Hand-built glyphs have one validation hole.** `IconGlyph` does not validate its view box, and
`default(IconViewBox)` bypasses the constructor entirely — so `new IconGlyph(default, layers)` is accepted
and yields a `0 0 0 0` box. The control then divides by a zero width, gets an infinite scale, rejects it and
paints **nothing**, silently. Always construct the view box explicitly, or use `IconViewBox.Default`:

```csharp
using Enigma.Icons;

var glyph = new IconGlyph(IconViewBox.Default, new[] { new IconLayer("M32,32 L224,224") });
```

## Exceptions

```csharp
using System;

namespace Enigma.Icons;

public sealed class IconNotFoundException : Exception
{
    public IconNotFoundException(string iconName, string? variant, string setName);
    public string IconName { get; }
    public string? Variant { get; }
    public string SetName { get; }        // e.g. "Phosphor" — from IIconSet.Name
}

public sealed class SvgParseException : Exception    // a broken source, not a miss
{
    public SvgParseException(string message);
    public SvgParseException(string message, Exception innerException);
}
```

`IconNotFoundException` echoes the caller's original strings **on the string surface only**; the typed
`GetGlyph(PhosphorIcon, PhosphorWeight)` overload reports the canonical kebab name and canonical weight
name instead. A broken source surfaces as `InvalidDataException` (corrupt embedded resource) or, from
`SvgIconSet`, as `SvgParseException` wrapping the underlying `IOException`.

Note which exception you will actually catch from the markup extensions and from `GetGlyph` with a bad
enum value: **`ArgumentOutOfRangeException`**, thrown by `ValidateWeight` or
`PhosphorIconNames.ToKebabCase` before any lookup happens. `IconNotFoundException` is documented as
unreachable for the Phosphor set in a correctly generated package, so `catch (IconNotFoundException)`
around a Phosphor lookup catches almost nothing.

## Common mistakes

- **Feeding `Image.Source` / `Path.Data` without restoring the view box** → mis-sized icons; a `Minus` at
  24 × 24 is a 24 × 2 sliver.
- **`Enum.ToString()` / `Enum.Parse` on `PhosphorIcon`** → the one hard-banned pattern. Use
  `PhosphorIconNames`. This includes binding a `string` straight to `Icon.Kind`, which routes through
  Avalonia's reflection-based enum conversion — convert in the ViewModel with `TryParse` instead.
- **`new IconGlyph(default, …)`** → a `0 0 0 0` view box and a silently invisible icon. Pass
  `IconViewBox.Default`.
- **`catch (IconNotFoundException)` around a Phosphor lookup** → the real exception for a bad enum value is
  `ArgumentOutOfRangeException`.
- **Asking Phosphor for variant `"DuoTone"` or `"duo-tone"`** → a miss. Only `"duotone"` (any case, trimmed)
  resolves.
- **`PhosphorWeight` left at `default`** → `Thin`, silently. Write `Regular` explicitly.
- **`ToGeometry` for duotone** → solid backing layer. Use `ToDrawing` / `ToDrawingImage`.
- **Calling `ToGeometry` per render/per item** → it parses every time. Cache it, or use the control (which
  caches per glyph internally).
- **Mutating a `Geometry` you assume is shared** → it is not shared; each call returns a fresh object.
  Conversely, do not assume two calls return the *same* object.
- **Treating `TryGetGlyph` as an exception guard** → it swallows misses only; corruption and undefined
  enum values still throw.
- **Assuming `IconLayer.Fill == null` means "not filled"** → null means *inherit the brush*. Only `"none"`
  disables the fill.
- **Reading `IconGlyph.IsSingleLayer` to decide whether to flatten** → it also requires full opacity and
  no stroke, which is stricter than `Layers.Count == 1`. `ToGeometry` deliberately branches on the count.
