---
name: enigma-icons-avalonia
description: Use when adding, rendering, theming or binding icons in an Avalonia app with the Enigma.Icons.Avalonia library (NuGet packages Enigma.Icons.Avalonia / Enigma.Icons.Phosphor / Enigma.Icons) — including adopting it into an app that does not reference it yet — spanning the ei:Icon control, the {ei:IconGeometry} and {ei:IconImage} markup extensions, ToGeometry / ToDrawing / ToDrawingImage, the 1,512 × 6 Phosphor artwork set, SvgIconSet over your own .svg files, and implementing a custom IIconSet.
metadata:
  version: "3.0.1"
---

# Enigma.Icons.Avalonia

Icons for **Avalonia 12**, published on nuget.org as `Enigma.Icons.Avalonia` **1.0.0** (with
`Enigma.Icons.Phosphor` and `Enigma.Icons`, also 1.0.0) — repo `josueclement/Enigma.Icons`. Targets
`net8.0` and `net10.0`.

Three packages, one dependency chain — you reference the top one and get all three:

| You want | Package | TFMs |
|---|---|---|
| The model, the SVG parser, your own `.svg` files | `Enigma.Icons` (zero dependencies) | `netstandard2.0`, `net8.0`, `net10.0` |
| The Phosphor artwork — 1,512 icons × 6 weights | `Enigma.Icons.Phosphor` (+ `Enigma.Icons`) | `netstandard2.0`, `net8.0`, `net10.0` |
| Avalonia rendering — the control, markup extensions, `Geometry` | **`Enigma.Icons.Avalonia`** (+ `Avalonia`) | `net8.0`, `net10.0` |

`Enigma.Icons.Avalonia` has **no** `netstandard2.0` target and **no** third-party dependency beyond
`Avalonia` itself (floor **12.1.0**) — no MVVM toolkit, no theme package, nothing to merge.

## Install

```bash
dotnet add package Enigma.Icons.Avalonia      # brings Enigma.Icons.Phosphor + Enigma.Icons + Avalonia
```

One namespace declaration reaches the control **and** both markup extensions:

```xml
xmlns:ei="https://github.com/josueclement/Enigma.Icons"
```

> **Nothing goes into `App.axaml`.** `Icon` derives from `Control`, not `TemplatedControl`, and renders
> itself in `Render`. The package ships **no XAML and no theme resources** — there is no
> `StyleInclude`/`ResourceInclude` to add and no resource key to get wrong. Add the package, declare the
> prefix, use the control.

The `using:` route is the documented fallback and needs **two** prefixes, because Avalonia's `using:`
mapping covers one CLR namespace and not its sub-namespaces:
`xmlns:ei="using:Enigma.Icons.Avalonia"` plus `xmlns:eim="using:Enigma.Icons.Avalonia.Markup"`. Note the
`ei` URI maps **only** those two Avalonia namespaces — `IIconSet` and `SvgIconSet` live in
`Enigma.Icons` and need their own `xmlns:eic="using:Enigma.Icons"`.

## The one decision in this library: control or markup extension?

A markup extension is evaluated **once, at load time**, so it can never follow a bound brush, a
`DynamicResource` or a theme switch — structurally, not by choice. The control resolves its brush at
render time, so it can.

**Prefer `<ei:Icon>` unless the slot's type forbids it.** Beyond theming, it is the only path that maps
the glyph's `0 0 256 256` view box; the extension methods drop it (see the trap below).

| Slot | Its type | Use |
|---|---|---|
| `Button.Content`, `MenuItem.Icon`, any `object` content | `object` | **`<ei:Icon/>`** |
| `Path.Data`, `PathIcon.Data` | `Geometry` | `{ei:IconGeometry}` / `ToGeometry()` |
| `Image.Source` | `IImage` | `{ei:IconImage}` / `ToDrawingImage()` — **set `Viewbox`** |
| `ImageBrush.Source` | `IImageBrushSource` | **nothing** — `DrawingImage` is not one |
| `Window.Icon`, `TrayIcon.Icon` | `WindowIcon` | **nothing** — ship a `.ico`/`.png`, or rasterize yourself |

`ei:Icon` is a `Control`, **not** an `IImage`, so it cannot go where Avalonia wants an image.

```xml
<ei:Icon Kind="Acorn" Weight="Duotone" Size="24" />                          <!-- themed, bound, duotone -->
<PathIcon Data="{ei:IconGeometry Acorn, Weight=Bold}" Width="16" Height="16" />       <!-- static only -->
```

The second deliberate asymmetry: the markup extensions **fail fast** (a bad enum value throws from
`ProvideValue` at load time), while `Icon.Render` **never throws** and silently paints nothing, so a
broken icon cannot take down the XAML previewer's surface for the whole window.

## The `Icon` control

| Property | Type | Default | Notes |
|---|---|---|---|
| `Kind` | `PhosphorIcon` | `Acorn` (enum 0) | Ignored while `IconSet` is set |
| `Weight` | `PhosphorWeight` | `Regular` | `Thin`, `Light`, `Regular`, `Bold`, `Fill`, `Duotone` |
| `IconSet` | `IIconSet?` | `null` | When non-null it **wins over** `Kind`/`Weight` |
| `IconName` | `string?` | `null` | Resolved against `IconSet` |
| `Variant` | `string?` | `null` | `null` = the set's `DefaultVariant` |
| `Foreground` | `IBrush?` | **inherits**; `Brushes.Black` where nothing sets it | Every layer paints with it |
| `Size` | `double` | `16` | Desired square; an explicit `Width`/`Height` wins |
| `Stretch` | `Stretch` | `Uniform` | `None`, `Uniform`, `UniformToFill`, `Fill` |

`Foreground` re-owns `TextElement.ForegroundProperty`, which **inherits** — so an icon inside a
`Button`, `MenuItem` or `TextBlock` picks up that scope's brush and follows a theme switch **with no
binding written by you**. That is the whole reason to prefer the control.

```xml
<Button>
  <StackPanel Orientation="Horizontal" Spacing="6">
    <ei:Icon Kind="Trash" VerticalAlignment="Center" />   <!-- takes the button's foreground, all states -->
    <TextBlock Text="Delete" VerticalAlignment="Center" />
  </StackPanel>
</Button>
```

All eight properties are `StyledProperty`, so `<Style Selector="ei|Icon">` sets house-wide defaults and
`Classes` variants work normally.

## Quick reference

| Task | API | Reference |
|---|---|---|
| Add the package, wire the prefix, test headlessly | — | `reference/setup.md` |
| Every `Icon` property, the `Stretch` maths, styling, accessibility | `Icon` | `reference/icon-control.md` |
| `Path.Data` / `Image.Source` from XAML, and the view-box trap | `…Avalonia.Markup` | `reference/markup-extensions.md` |
| Glyph → `Geometry` / `Drawing` / `DrawingImage`, lookups, the model | `IconGlyphExtensions` | `reference/csharp-api.md` |
| Your own `.svg` files, shipping them, a custom `IIconSet` | `SvgIconSet`, `IIconSet` | `reference/custom-icon-sets.md` |
| Theme variants, duotone, thousands of icons, trimming, startup cost | — | `reference/theming-and-performance.md` |

## Cross-cutting conventions

- **Name lookup is forgiving; variant lookup barely is.** Every string API accepts kebab-case,
  `snake_case` or PascalCase case-insensitively (`"arrow-right"`, `"Arrow_Right"`, `"ArrowRight"` are the
  same icon). For Phosphor **variants**, only trimming and case-insensitivity help — `"Duotone"` and
  `" DUOTONE "` hit, but `"DuoTone"`, `"duo-tone"` and `"duo_tone"` all **miss**, because no weight name
  contains a hyphen. And a variant the set does not have is a **miss, never a silent fallback**.
- **`Try` governs absence, not corruption.** `TryGetGlyph` returns `false` for an icon that is not there,
  but a *broken source* — malformed SVG, a vanished file, a corrupt resource, an undefined enum value —
  throws from `TryGetGlyph` exactly as it does from `GetGlyph`. It is not a general exception swallow.
- **Never `Enum.ToString()` / `Enum.Parse` on a `PhosphorIcon`.** Use `PhosphorIconNames.ToKebabCase`,
  `PhosphorIconNames.TryParse` and `PhosphorIconNames.All` — the trimming-safe, allocation-cheap path over
  1,512 members. This includes not binding a `string` to `Kind`: convert in the ViewModel instead.
- **Glyphs are immutable and handed out reference-equal**, and the geometry cache is keyed on the glyph
  instance. A custom `IIconSet` that returns a fresh `IconGlyph` per call silently costs a
  `Geometry.Parse` (~34 µs) per icon per render pass.
- **Every layer paints with the caller's brush.** A layer's own `fill` is ignored (only the literal
  `"none"` disables filling); a layer's own `stroke` *is* honoured when it names a parseable colour.

## Gotchas that cost real time

1. **`ToDrawingImage` / `ToGeometry` drop the view box, so icons come out inconsistently sized.** They
   report the *tight ink bounds*, not `0 0 256 256`: `Minus` measures 184 × 16 and `DotOutline` 32 × 48, so
   `<Image Source="{ei:IconImage Minus}" Width="24" Height="24"/>` renders a **24 × 2 sliver**. Every icon
   zooms its own bounding box into the slot, so a toolbar built this way has no shared optical grid. Fix it
   by setting `DrawingImage.Viewbox = new Rect(0, 0, 256, 256)` (there is no library API for it), or use
   `<ei:Icon>`, which maps the view box correctly.
2. **A bare `<ei:Icon/>` draws a black acorn.** `Kind`'s default is enum 0 = `Acorn`, and `Foreground`'s
   registered default is `Brushes.Black` — so an unset icon on a dark theme is a black-on-black acorn, not
   nothing. Always set `Kind`, and set `Foreground` where there is no text scope to inherit from.
3. **`default(PhosphorWeight)` is `Thin`, not `Regular`.** Every API defaults the weight to `Regular`
   *explicitly*, so this only bites C# that writes `default` or leaves a field uninitialised — silently, as
   thin artwork.
4. **`{ei:IconImage}` defaults its `Brush` to black**, and being a markup extension it can never follow the
   variant. Set `Brush` explicitly, or use the control.
5. **`ToGeometry` and `{ei:IconGeometry}` lose per-layer opacity, stroke metadata and the fill rule**, so
   `Duotone` comes out with a solid backing shape. Use `ToDrawing`, `ToDrawingImage`, `{ei:IconImage}` or
   the control for anything multi-layer or stroked.
6. **The markup extensions are Phosphor-only.** They have no `IconSet` route. To drive Phosphor *by string*
   through the control, set `IconSet="{x:Static ph:PhosphorIconSet.Instance}"` and bind `IconName` — but
   note that on that path **`Variant` is live and `Weight` is dead**, the exact inverse of the `Kind` path.
7. **`IconSet` set with an empty `IconName` draws nothing, and does not fall back to `Kind`.** Binding an
   `IconSet` before its name is populated yields a blank.
8. **`Icon.Render` never throws, so a typo'd `IconName` is a silent blank.** There is no logging. Assert the
   name in a test with `GetGlyph`, which throws.
9. **Only `UniformToFill` is clipped.** `Stretch="None"` draws a Phosphor glyph at its natural 256 DIP and
   paints straight over its neighbours; add `ClipToBounds="True"` on the parent.
10. **The first lookup in each weight costs ~10 ms synchronously**, on whatever thread touches it — normally
    the UI thread during the first render pass. Nothing is ever evicted. See
    `reference/theming-and-performance.md` for the warm-up recipe.
11. **`AVLN*` XAML warnings are not promoted by `TreatWarningsAsErrors`** (they come from an MSBuild task),
    so a build can print `Build succeeded` while carrying them. Read the warning count on any project that
    compiles `.axaml`.

## When NOT to use

- **Non-Avalonia UIs** — WPF, WinForms, MAUI, web. A WPF sibling is deferred and does not exist; use
  `Enigma.Icons` + `Enigma.Icons.Phosphor` directly and convert `IconLayer.PathData` yourself.
- **`netstandard2.0` consumers** — the two lower packages support it, this one cannot (Avalonia 12 ships
  `net8.0`/`net10.0` assets only).
- **Window icons, tray icons, native menu icons, or `ImageBrush`** — those need a `WindowIcon`, a `Bitmap`
  or an `IImageBrushSource`. Nothing in this library produces one; ship a `.ico`/`.png` instead.
- **Runtime-loaded remote SVG, animation, RTL mirroring, or multicolour artwork.** The parser handles a
  static SVG subset, every layer is recoloured with one brush, and `Render` ignores `FlowDirection`.
- **Size-critical apps that need only a handful of icons** — the artwork is ~3.9 MB of embedded resources
  and trimming cannot subset it.

Read the relevant `reference/*.md` for the full public API, a runnable example, and the mistakes that
actually happen.
