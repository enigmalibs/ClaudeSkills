# The markup extensions

Two `MarkupExtension` subclasses in `Enigma.Icons.Avalonia.Markup`, both reached through the same `ei`
prefix as the control:

```xml
<Path  Data="{ei:IconGeometry Acorn, Weight=Bold}" Fill="Black" Stretch="Uniform" />
<Image Source="{ei:IconImage Acorn, Weight=Fill, Brush=Red}" Width="24" Height="24" />
```

Read the view-box section below before you use either one in a row of icons — it is the defect that
catches everybody.

## When to use them — and when not to

**A markup extension is evaluated once, at load time.** It returns a plain object; there is no live
channel back to the XAML. It therefore *cannot* follow a bound brush, a `DynamicResource`, or a
light/dark variant switch. Not a design compromise — structurally impossible.

| Situation | Use |
|---|---|
| Colour is bound, themed, inherited, or changes on hover | **`<ei:Icon>`** |
| Several icons that must look the same size | **`<ei:Icon>`** (see below) |
| `Duotone`, or any multi-layer or stroked glyph | **`<ei:Icon>`** or `{ei:IconImage}` |
| A custom `IIconSet` / your own SVGs | **`<ei:Icon>`** (extensions are Phosphor-only) |
| A static `Geometry` slot — `Path.Data`, `PathIcon.Data` | `{ei:IconGeometry}` |
| A static `IImage` slot — `Image.Source` | `{ei:IconImage}` |

Reach for an extension when the slot's *type* demands it — a control exposing `Geometry?` or `IImage?`
rather than accepting arbitrary content.

**Prefer `PathIcon` over a bare `Path`.** `PathIcon.Data` is a `Geometry` too, but `PathIcon` is a
`TemplatedControl` with a themeable, inheriting `Foreground`, so you get the control's theming story back
without binding `Fill` yourself:

```xml
<PathIcon Data="{ei:IconGeometry Trash}" Width="16" Height="16" />
```

## The view box is dropped — the trap that produces visibly wrong UI

Every Phosphor glyph is authored in a `0 0 256 256` view box, and `<ei:Icon>` maps that box into its
bounds. **Neither extension does.** `ToDrawingImage` never sets `DrawingImage.Viewbox`, and a `Geometry`
carries no view box at all, so both report the glyph's **tight ink bounds** instead. Measured against
Avalonia 12.1.0:

| Icon (`Regular`) | `glyph.ViewBox` | `DrawingImage.Size` / `ToGeometry().Bounds` |
|---|---|---|
| `Acorn` | 0 0 256 256 | 208 × 232 |
| `Star` | 0 0 256 256 | 217.47 × 203.42 |
| `Minus` | 0 0 256 256 | **184 × 16** |
| `DotOutline` | 0 0 256 256 | **32 × 48** |

Consequences:

- `<Image Source="{ei:IconImage Minus}" Width="24" Height="24"/>` renders a **24 × 2 sliver**, because
  `Image` scales `DrawingImage.Size` (184 × 16) uniformly into 24 × 24. `DotOutline` renders as a tall pill.
- `Path.Stretch` and `PathIcon` use geometry bounds too, so a toolbar built from `{ei:IconGeometry}` has
  **no shared optical grid** — each icon zooms its own bounding box to the slot — and its icons are
  mutually misaligned with any `<ei:Icon>` of the same `Size`.

**The fix for `Image`** (verified: it restores `Size` to 256 × 256) — note there is no library API for
this, and `{ei:IconImage}` has no `Viewbox` property, so it only works from code:

```csharp
using Avalonia;
using Avalonia.Media;
using Enigma.Icons.Avalonia;
using Enigma.Icons.Phosphor;

DrawingImage img = PhosphorIconSet.Instance
    .GetGlyph(PhosphorIcon.Minus)
    .ToDrawingImage(Brushes.Black);

img.Viewbox = new Rect(0, 0, 256, 256);      // Rect? — now Size is 256 × 256 and the icon shares the grid
```

For `Path`/`PathIcon` there is **no** fix through `ToGeometry` — you cannot add a transparent 256 × 256
spacer to the returned geometry through the public API. Give the `Path` a fixed `Width`/`Height` and accept
per-icon variation, or use `<ei:Icon>`.

**Rule of thumb: for anything in a row, grid or toolbar of icons, use the control.**

## `IconGeometryExtension` → `{ei:IconGeometry}`

```csharp
using System;
using Avalonia.Markup.Xaml;
using Enigma.Icons.Phosphor;

namespace Enigma.Icons.Avalonia.Markup;

public sealed class IconGeometryExtension : MarkupExtension
{
    public IconGeometryExtension();                       // Icon = default(PhosphorIcon) = Acorn
    public IconGeometryExtension(PhosphorIcon icon);      // the positional form
    public PhosphorIcon Icon { get; set; }
    public PhosphorWeight Weight { get; set; } = PhosphorWeight.Regular;
    public override object ProvideValue(IServiceProvider serviceProvider);   // returns Geometry
}
```

Equivalent to `PhosphorIconSet.Instance.GetGlyph(Icon, Weight).ToGeometry()`.

```xml
<PathIcon Data="{ei:IconGeometry Acorn}" Width="26" Height="26" />

<Path Data="{ei:IconGeometry Acorn}" Fill="{DynamicResource TextFillColorPrimaryBrush}"
      Stretch="Uniform" Width="26" Height="26" />
```

Note what is themed in the second form: the **`Path`'s `Fill`**, not the extension. The extension supplies
geometry, which is colourless — a perfectly good pattern, and the one case where an extension coexists with
a theme switch, because the colour never went through it.

**A multi-layer glyph loses per-layer opacity, stroke metadata and the fill rule.** `ToGeometry` collapses
it into a `GeometryGroup`, which has no per-child opacity and one shared fill rule (taken from the *first*
layer). A `Duotone` glyph therefore paints its 20 %-opacity backing shape solid. A **one-layer** glyph that
is stroked or translucent fares no better: it collapses to the bare parsed path and its stroke and opacity
are dropped silently. **Do not use `{ei:IconGeometry}` with `Weight=Duotone`** or with stroked custom
artwork.

A `Path` with no `Stretch` draws the geometry at its natural 256-unit scale.

## `IconImageExtension` → `{ei:IconImage}`

```csharp
using System;
using Avalonia.Markup.Xaml;
using Avalonia.Media;
using Enigma.Icons.Phosphor;

namespace Enigma.Icons.Avalonia.Markup;

public sealed class IconImageExtension : MarkupExtension
{
    public IconImageExtension();
    public IconImageExtension(PhosphorIcon icon);
    public PhosphorIcon Icon { get; set; }
    public PhosphorWeight Weight { get; set; } = PhosphorWeight.Regular;
    public IBrush Brush { get; set; } = Brushes.Black;          // <-- note the default
    public override object ProvideValue(IServiceProvider serviceProvider);   // returns DrawingImage
}
```

Equivalent to `PhosphorIconSet.Instance.GetGlyph(Icon, Weight).ToDrawingImage(Brush)`.

```xml
<!-- Brush set explicitly: the default is black, which is invisible on a dark theme, and a markup
     extension can never follow the variant. -->
<Image Source="{ei:IconImage Acorn, Brush=DodgerBlue}" Width="26" Height="26" />
```

It goes through `ToDrawing`, so **per-layer opacity is preserved** — `{ei:IconImage Heart, Weight=Duotone}`
renders correctly, unlike `{ei:IconGeometry}`. It still drops the view box (above).

`DrawingImage` implements `IImage`, so it fits `Image.Source`. It does **not** implement
`IImageBrushSource`, so `<ImageBrush Source="{ei:IconImage …}"/>` will not bind, and it is not a
`WindowIcon`, so it cannot be a window or tray icon.

**Why `IconImage` and not `IconSource`.** It returns a `DrawingImage`, and Avalonia has its own unrelated
`IconSource` concept. The retired `PhosphorIconsAvalonia` package called this `IconSourceExtension` and
misled people into expecting an `IconSource`; the rename is the deliberate, most visible break from that
API. Porting from that package: `IconSourceExtension` → `IconImageExtension`.

## They fail fast — the opposite of the control

`ProvideValue` resolves the glyph eagerly, so a bad value throws at XAML load time. A bad value in markup is
an authoring error you want to see immediately; `Icon.Render` deliberately paints nothing instead, to keep
the previewer alive.

**The exception you will actually see is `ArgumentOutOfRangeException`, not `IconNotFoundException`** —
`GetGlyph` validates the enum values first (`ValidateWeight`, then `PhosphorIconNames.ToKebabCase`), and
`IconNotFoundException` is documented as unreachable in a correctly generated package. Both XML doc
comments advertise only `IconNotFoundException`, so a `catch (IconNotFoundException)` around a XAML load
will miss the real failure.

In practice you cannot reach either from hand-written XAML: both properties are typed `PhosphorIcon` /
`PhosphorWeight`, so a misspelled member fails in the Avalonia XAML compiler as a build error. The runtime
exceptions need a cast integer, which only C# can express.

Practical effect: a broken `{ei:IconGeometry …}` takes down the whole window's load, not just the icon.
That is intended — but it means the extensions are the wrong tool for a name that comes from data.

## One shared instance per setter — the mutation trap

A markup extension in a `Style` or `ControlTheme` setter is evaluated **once**, and the resulting object is
shared by **every** target the setter applies to. `Geometry.Transform` and `DrawingImage.Viewbox` are
publicly settable, so one consumer mutating the value moves or resizes every icon that setter touched.

```xml
<!-- One Geometry instance shared by every Button in scope. -->
<Style Selector="Button.icon">
  <Setter Property="Tag" Value="{ei:IconGeometry Gear}" />
</Style>
```

`ToGeometry`'s per-call freshness protects direct C# callers only — it cannot protect the single instance a
setter produced. If you need to mutate, call `ToGeometry()` yourself per use site.

## Common mistakes

- **Using either extension for a row of icons** → inconsistent sizes and a 24 × 2 `Minus`. Use the control,
  or set `DrawingImage.Viewbox` from code.
- **`{ei:IconImage …}` with no `Brush`** → a black icon, invisible on a dark theme.
- **`{ei:IconGeometry Acorn, Weight=Duotone}`** → the backing layer paints solid. Use `{ei:IconImage}` or
  the control.
- **Expecting an extension to follow a theme switch** → it cannot. Theme the *consuming* property
  (`Path.Fill`, or `PathIcon.Foreground`) or use the control.
- **`catch (IconNotFoundException)`** around a load → the real exception is `ArgumentOutOfRangeException`.
- **Looking for `IconSet` / `IconName` on an extension** → they do not exist. Custom sets reach XAML only
  through `<ei:Icon IconSet="…" IconName="…"/>`.
- **`<ImageBrush Source="{ei:IconImage …}"/>` or `<Window.Icon><ei:Icon/></Window.Icon>`** → wrong types
  entirely; neither is supported.
- **A `Path` with `{ei:IconGeometry}` and no `Stretch`** → drawn at the 256-unit natural size.
- **Mutating a geometry that came from a `Style` setter** → every target changes.
- **One `xmlns:ei="using:Enigma.Icons.Avalonia"`** → the extensions live in the `.Markup` sub-namespace and
  will not resolve. Use the URI form (`setup.md` §2).
