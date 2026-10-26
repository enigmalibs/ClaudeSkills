# Theming, duotone and performance

The two cross-cutting concerns: making an icon follow a light/dark switch, and rendering a lot of icons
without paying for them twice.

## Making an icon follow the theme

Three mechanisms, in order of preference:

**1. Inherit — write nothing.** `Icon.Foreground` re-owns `TextElement.ForegroundProperty`, which is an
inheriting property. An icon inside any text scope takes that scope's brush, including its hover/pressed
states, and follows a variant switch with no binding at all.

```xml
<Button>
  <StackPanel Orientation="Horizontal" Spacing="6">
    <ei:Icon Kind="FloppyDisk" VerticalAlignment="Center" />
    <TextBlock Text="Save" VerticalAlignment="Center" />
  </StackPanel>
</Button>
```

**2. `DynamicResource`** when there is no scope to inherit from:

```xml
<ei:Icon Kind="Gear" Foreground="{DynamicResource SystemControlForegroundBaseHighBrush}" />
```

**3. A binding** when the colour is app state rather than theme state:

```xml
<ei:Icon Kind="Circle" Foreground="{Binding StatusBrush}" />
```

What does **not** work:

- **`StaticResource`** freezes the brush at load time. The icon keeps the old variant's colour after a
  switch. Always `DynamicResource`.
- **Both markup extensions**, structurally — they are evaluated once at load time. `{ei:IconImage}`'s
  `Brush` in particular defaults to **black**, invisible on a dark theme.
- **Any `IImage` slot.** `ToDrawingImage` bakes the brush into its `GeometryDrawing`s, so an `Image.Source`
  built from this library is permanently un-themed. No converter, observable or helper ships — the public
  surface is exactly four types. Rebuild the `DrawingImage` yourself on a variant change, or use the
  control.
- **A `Path` fed by `{ei:IconGeometry}`** — but only for the geometry. Theme the `Path.Fill` (or use
  `PathIcon`, whose `Foreground` inherits) and it works fine, because the colour never went through the
  extension.

Set `RequestedThemeVariant="Default"` on the `Application` during development — following the OS
preference is what actually exercises this.

### `Foreground`'s default is black, not null

`Foreground`'s **registered default is `Brushes.Black`** (inherited from `TextElement`), and it inherits.
So:

- A bare `<ei:Icon Kind="Gear"/>` outside any text scope paints a **black** icon — on a dark theme that
  reads as "my icon is missing", but the cause is colour, not resolution.
- An **unresolved** `DynamicResource` reverts the property to that registered default, so a typo'd resource
  key also yields a black icon, never an invisible one.
- `Foreground` is `null` only when something sets it to null explicitly — `{x:Null}`, a null-producing
  binding, or `Foreground = null` in code. *Then* `Render` returns before drawing anything, with no black
  fallback.

Debugging "my icon is the wrong colour or looks missing": check for black-on-dark first, and an explicit
null second.

### There is no theme-aware weight selection

Nothing in the library switches `Kind` or `Weight` by variant. If you want `Fill` in dark and `Regular` in
light, write a style with a variant selector or wrap the subtree in a `ThemeVariantScope` yourself.

## Styling is the lever nobody expects

All eight properties are `StyledProperty` (none is a `DirectProperty`), so ordinary Avalonia styling works —
this is the right way to set house-wide icon defaults:

```xml
<Style Selector="ei|Icon">
  <Setter Property="Size" Value="20" />
  <Setter Property="Weight" Value="Bold" />
</Style>

<Style Selector="ei|Icon.large">
  <Setter Property="Size" Value="32" />
</Style>

<!-- Foreground animates, because it is a StyledProperty -->
<Style Selector="ei|Icon">
  <Setter Property="Transitions">
    <Transitions><BrushTransition Property="Foreground" Duration="0:0:0.15" /></Transitions>
  </Setter>
</Style>
```

The trap: a `<Setter Property="IconSet" …/>` in a broad selector **kills every `Kind`-based icon in
scope**, because a non-null `IconSet` wins unconditionally. Scope such a setter to a class.

`Icon.Render` also ignores `FlowDirection`, so icons do **not** mirror in RTL layouts. Mirror them yourself
with a `ScaleTransform` where it matters.

## Duotone

`PhosphorWeight.Duotone` is a **two-layer** glyph: a tinted backing shape at 20 % opacity behind the
foreground shape. Whether that survives depends entirely on which API you go through, because a
`GeometryGroup` has no per-child opacity.

| API | Duotone |
|---|---|
| `<ei:Icon Weight="Duotone">` | **correct** — walks the layers, pushes each one's opacity |
| `ToDrawing` / `ToDrawingImage` | **correct** — wraps a translucent layer in its own `DrawingGroup` |
| `{ei:IconImage Weight=Duotone}` | **correct** (goes through `ToDrawing`) |
| `ToGeometry` | **wrong** — backing shape paints solid |
| `{ei:IconGeometry Weight=Duotone}` | **wrong** (goes through `ToGeometry`) |

The same applies to any multi-layer glyph from your own SVGs, and to a *one-layer* glyph that is stroked or
translucent — `ToGeometry` drops its stroke and opacity too. If a slot demands a single `Geometry`, duotone
cannot be represented there; pick another weight.

## What is cached, and where

Two independent caches, both process-wide and both invisible:

**1. Glyph resolution (in the icon set).** `PhosphorIconSet` loads a weight's table on **first use of that
weight** and keeps it for the process's life; each resolved `IconGlyph` is cached, so repeated lookups return
the **same instance**. Nothing is read when you touch `Instance`. Both caches are `ConcurrentDictionary`, so
every member is thread-safe.

**2. Parsed geometry (in the Avalonia layer).** An internal `ConditionalWeakTable<IconGlyph, Geometry[]>`
keyed on the **glyph instance**, so path data is parsed **once per glyph, not once per render pass**. A
resize, a theme switch, or a scroll through a virtualized list re-renders every visible icon at no parsing
cost, and many controls showing the same icon share one parse. The keys are weak: a custom `IIconSet` that
goes out of scope takes its glyphs and their geometry with it.

Three consequences worth knowing:

- **The cache is why an `IIconSet` must return reference-equal glyphs.** A set that builds a fresh
  `IconGlyph` per call turns every render pass into a `Geometry.Parse` — measured at ~34 µs per glyph, with
  no error and no log to trace it by.
- **All layers are parsed eagerly** on the first request for a glyph, including layers a paint pass skips.
  So a glyph with one malformed layer paints *nothing* rather than a partial glyph — and a failed glyph is
  **not** cached, so it re-parses and re-fails on **every render pass**.
- **`ToGeometry` / `ToDrawing` / `ToDrawingImage` do NOT use this cache.** They parse afresh on every call
  and hand you an independent, mutable object. Never call them per item or inside a converter; cache the
  result, or use the control.

## Measured costs

Against `net10.0` Release, headless, warm process:

| Operation | Cost |
|---|---|
| **First lookup in a weight** (loads and splits that weight's whole `.dat`) | **~9.6 ms**, synchronous |
| Any warm lookup | ~0.03 ms |
| Materializing all 1,512 `Regular` glyphs | 6.2 ms, ~530 KB retained |
| `Geometry.Parse` for all 1,512 glyphs | 51 ms (~34 µs each) |

**The ~10 ms hits the thread that touches the weight first** — normally the UI thread, during the first
render pass. Two weights on one screen is two hits. There is **no warm-up API**, but both caches are
`ConcurrentDictionary`, so you can prime them off-thread at startup:

```csharp
using System.Threading.Tasks;
using Enigma.Icons.Phosphor;

// Startup, off the UI thread: absorbs the per-weight table load before the first frame.
_ = Task.Run(() =>
{
    foreach (PhosphorWeight weight in new[] { PhosphorWeight.Regular, PhosphorWeight.Fill })
    {
        PhosphorIconSet.Instance.GetGlyph(PhosphorIcon.Acorn, weight);
    }
});
```

Honest caveat: this removes the table-load spike only. The geometry cache is filled inside `Render` on the
UI thread, so the ~34 µs-per-glyph parse still lands on the first frame.

**Nothing is ever evicted, and there is no way to release it.** Neither set exposes `Clear`, `Reset` or
`Dispose`. A weight picker that touches all six tables permanently retains ~3.9 MB of strings plus every
glyph it materialized.

## Rendering hundreds or thousands of icons

Each `<ei:Icon>` is a full `Control` — layout, visual, automation peer — but with no template, no visual
children and cached geometry, so the usual Avalonia list rules are the whole story: virtualize.

Avalonia 12 ships exactly one general-purpose virtualizing panel, `VirtualizingStackPanel`, and it is
one-dimensional. A virtualized *grid* is therefore a virtualized list of rows, each row a non-virtualizing
`UniformGrid`:

```xml
<ScrollViewer HorizontalScrollBarVisibility="Disabled" VerticalScrollBarVisibility="Auto">
  <ItemsControl ItemsSource="{Binding Rows}">
    <ItemsControl.ItemsPanel>
      <ItemsPanelTemplate><VirtualizingStackPanel /></ItemsPanelTemplate>
    </ItemsControl.ItemsPanel>
    <ItemsControl.ItemTemplate>
      <DataTemplate x:DataType="vm:IconRow">
        <ItemsControl ItemsSource="{Binding Cells}">
          <ItemsControl.ItemsPanel>
            <ItemsPanelTemplate><UniformGrid Columns="8" /></ItemsPanelTemplate>
          </ItemsControl.ItemsPanel>
          <ItemsControl.ItemTemplate>
            <DataTemplate x:DataType="vm:IconEntry">
              <ei:Icon Kind="{Binding Kind}" HorizontalAlignment="Center"
                       Weight="{Binding $parent[Window].((vm:MainWindowViewModel)DataContext).SelectedWeight}"
                       Size="{Binding $parent[Window].((vm:MainWindowViewModel)DataContext).IconSize}" />
            </DataTemplate>
          </ItemsControl.ItemTemplate>
        </ItemsControl>
      </DataTemplate>
    </ItemsControl.ItemTemplate>
  </ItemsControl>
</ScrollViewer>
```

Bind shared appearance (`Weight`, `Size`, `Foreground`) **up** to the parent ViewModel rather than baking it
into each item. Because those properties are registered with `AffectsRender`/`AffectsMeasure`, changing one
repaints the already-realized controls; rebuilding the list would be far more expensive.

In dense grids: stick to **one weight** (each is a separate table load) and avoid `Duotone`, which doubles
the draw calls and adds a `PushOpacity` per icon.

Build the item catalogue with the generated name table, never `Enum.Parse`. `PhosphorIconNames.All` is in
enum order, so the index *is* the enum value:

```csharp
using System.Collections.Generic;
using Enigma.Icons.Phosphor;

public sealed record IconEntry(PhosphorIcon Kind, string Name);

IReadOnlyList<string> names = PhosphorIconNames.All;          // 1,512 kebab-case names
var catalog = new IconEntry[names.Count];
for (int i = 0; i < catalog.Length; i++)
{
    catalog[i] = new IconEntry((PhosphorIcon)i, names[i]);    // no reflection, no parsing
}
```

## Payload size, trimming and AOT

All three packages are `IsTrimmable` and `IsAotCompatible` on the modern TFMs and build free of
`IL2xxx`/`IL3xxx` warnings. The lookup path is genuinely clean: resource names come from a compile-time
literal plus an array index, never `Enum.GetName`/`ToString`/`Parse`, so trimming cannot break it.

**But trimming cannot shrink the artwork.** Measured in `bin/Release/net10.0`:

| Assembly | Size |
|---|---|
| `Enigma.Icons.Phosphor.dll` | **~4.06 MB** (six embedded `.dat` resources, ~3.95 MB) |
| `Enigma.Icons.dll` | ~44 KB |
| `Enigma.Icons.Avalonia.dll` | ~15 KB |

An app using three icons ships all 9,072. There is **no** subsetting mechanism, no per-weight package and no
source generator. It compresses well in the `.nupkg` and in a single-file bundle, but if that is
unacceptable, reference `Enigma.Icons` alone and ship your own `.svg` files — noting that
`Enigma.Icons.Avalonia` depends on `Enigma.Icons.Phosphor`, so using the control or the extension methods
always brings the artwork with it.

One trim/AOT hole to avoid in **your** code: binding a `string` straight to `Kind`
(`Kind="{Binding IconNameFromJson}"`) goes through Avalonia's built-in string→enum conversion, not the
generated tables. Convert in the ViewModel instead:

```csharp
using Enigma.Icons.Phosphor;

public PhosphorIcon Kind =>
    PhosphorIconNames.TryParse(_name, out PhosphorIcon icon) ? icon : PhosphorIcon.Question;
```

## Common mistakes

- **`Foreground="{StaticResource …}"`** → the icon keeps the old variant's colour after a theme switch.
- **Diagnosing a missing icon as a null `Foreground`** → the default is black; on a dark theme you are
  almost always looking at black-on-black.
- **Relying on a markup extension or an `IImage` to follow the theme** → neither can.
- **`ToGeometry` for duotone or stroked artwork** → opacity, stroke and fill rule are dropped.
- **A custom `IIconSet` returning fresh glyphs** → a `Geometry.Parse` per render pass, silently.
- **Calling `ToGeometry` in a converter or a per-item property** → parses per item, per evaluation.
- **Not priming the weights you use** → a ~10 ms UI-thread stall on the first frame, per weight.
- **A broad `<Setter Property="IconSet">`** → every `Kind`-based icon in scope goes blank.
- **A non-virtualizing panel for a long icon list** → thousands of realized controls.
- **Binding a `string` to `Kind`** → reflection-based enum conversion; use `PhosphorIconNames.TryParse`.
- **Expecting to unload a weight's table** → there is no eviction. Touching all six is a permanent ~3.9 MB.
