# The `ei:Icon` control

`Enigma.Icons.Avalonia.Icon` — a `sealed class Icon : Control` that overrides `MeasureOverride` and
`Render`. Not a `TemplatedControl`: no theme, no template, no resource keys, nothing in `App.axaml`.

This is the icon API you should reach for by default. The markup extensions exist for the narrow
static case; the control is the one that can follow a binding or a theme.

## Properties

Every property has a public `StyledProperty` identifier (`Icon.KindProperty`, `Icon.SizeProperty`, …)
so it can be styled, animated and bound like any Avalonia property.

| Property | Type | Default | Affects |
|---|---|---|---|
| `Kind` | `PhosphorIcon` | `default(PhosphorIcon)` = `Acorn` | render |
| `Weight` | `PhosphorWeight` | `Regular` (explicit, **not** `default`) | render |
| `IconSet` | `IIconSet?` | `null` | render |
| `IconName` | `string?` | `null` | render |
| `Variant` | `string?` | `null` | render |
| `Foreground` | `IBrush?` | **inherits**; `Brushes.Black` where nothing sets it | render |
| `Size` | `double` | `16.0` | render + **measure** |
| `Stretch` | `Stretch` | `Stretch.Uniform` | render + **measure** |

`Focusable` is overridden to `false` for `Icon`.

Because `Size` and `Stretch` are registered with `AffectsMeasure` and everything is registered with
`AffectsRender`, changing any of them on an **already-realized** control repaints it — you never need to
rebuild the visual tree to change a weight, a size or a colour.

## Glyph resolution — `IconSet` wins over `Kind`

```
IconSet is not null?
├── yes → IconName null or empty?  → draw NOTHING (no fall back to Kind)
│         else → IconSet.TryGetGlyph(IconName, Variant, out glyph)
└── no  → PhosphorIconSet.Instance.TryGetGlyph(Kind, Weight, out glyph)
```

Two consequences that catch people:

- **`Kind` and `Weight` are ignored the moment `IconSet` is non-null.** Setting both is not a fallback
  chain; it is one live path and one dead one.
- **`IconSet` bound before `IconName` yields a blank.** If a ViewModel exposes the set eagerly and the
  name asynchronously, the icon is empty until the name arrives — not an acorn.

`Variant = null` means the set's `DefaultVariant`. A variant the set does not have is a **miss**, never
a silent fallback to the default.

## `Foreground` inherits, and that is the whole point

`ForegroundProperty` is `TextElement.ForegroundProperty.AddOwner<Icon>()`. `TextElement.Foreground` is an
**inheriting** property, so an `Icon` placed in any text scope — a `Button`, `MenuItem`, `TextBlock`,
`ContentPresenter` — picks up that scope's brush automatically, including its hover and pressed states,
and follows a theme-variant switch **with no binding written by you**.

```xml
<Button>
  <StackPanel Orientation="Horizontal" Spacing="6">
    <ei:Icon Kind="Trash" VerticalAlignment="Center" />
    <TextBlock Text="Delete" VerticalAlignment="Center" />
  </StackPanel>
</Button>
```

**Where nothing sets it, `Foreground` is `Brushes.Black`, not null** — that is `TextElement`'s registered
default, and `Icon` does not override it. Three things follow:

- A bare `<ei:Icon Kind="Gear"/>` on a `Canvas`, `Border` or `Panel` with no text scope paints a **black**
  icon. On a dark theme that looks like a missing icon, but the cause is colour, not resolution.
- An **unresolved** `DynamicResource` reverts the property to that default, so a typo'd resource key also
  gives you black — never an invisible icon.
- `Foreground` is null only when something sets it to null: `{x:Null}`, a null-producing binding, or
  `Foreground = null` in code. *Then* `Render` returns before drawing anything, with no black fallback.

Set it explicitly when there is no scope to inherit from, and always with `DynamicResource` so it
follows the variant:

```xml
<ei:Icon Kind="Gear" Foreground="{DynamicResource SystemControlForegroundBaseHighBrush}" />
```

## Sizing

`MeasureOverride` **ignores `availableSize`** and returns `new Size(Size, Size)` — a square. If `Size` is
`NaN`, zero, negative or infinite it returns an empty size and nothing is drawn.

- **An explicit `Width`/`Height` wins over `Size`.** `Layoutable.MeasureCore` already coerces the
  measured result against `Width`/`Height`/`Min*`/`Max*`; the control deliberately adds no second
  precedence rule.
- **`Size` sets the *desired* size, not a ceiling.** `Render` scales into `Bounds`, and `Control` defaults
  to `HorizontalAlignment`/`VerticalAlignment` = `Stretch` — so in a stretching parent (a vertical
  `StackPanel`, a `Grid` cell) the control's bounds grow past `Size`. Under the default
  `Stretch="Uniform"` the glyph still *looks* `Size`-big because the scale is min-constrained, but it is
  centred inside a much larger hit area — and under `Fill` it visibly distorts. Set
  `HorizontalAlignment="Center"` / `VerticalAlignment="Center"` on icons inside stretching parents.

## `Stretch`

The glyph's view box (`0 0 256 256` for every Phosphor icon) is scaled into the control's bounds, then
centred. A view box whose origin is not `0,0` is offset correctly.

| Mode | Scale | Notes |
|---|---|---|
| `None` | `1.0` on both axes | **Natural view-box size** — 256 DIP for Phosphor. Not clipped. |
| `Uniform` *(default)* | `min(sx, sy)` on both | Fits inside, preserves aspect ratio |
| `UniformToFill` | `max(sx, sy)` on both | Fills, overflows — **the only mode `Render` clips** |
| `Fill` | `sx` and `sy` independently | Distorts to the exact bounds |

`Stretch="None"` on a Phosphor icon in a small box paints a 256 DIP glyph straight over its neighbours,
because only `UniformToFill` gets a clip. Wrap it:

```xml
<Border Width="96" Height="32" ClipToBounds="True">
  <ei:Icon Kind="Acorn" Stretch="None"
           HorizontalAlignment="Stretch" VerticalAlignment="Stretch" />
</Border>
```

## How layers are painted

The control walks `glyph.Layers` in order (index 0 first, i.e. bottom-most) and for each one:

- **Fill**: the control's `Foreground`, always. A layer's own `fill` value is *ignored* — only the
  literal `"none"` turns filling off. An icon that refused the caller's colour would be the bug this
  avoids.
- **Stroke**: the layer's own `stroke` when it names a colour Avalonia can parse, otherwise `Foreground`.
  This asymmetry is deliberate: a hand-authored SVG that says `stroke="red"` means it. The `Pen` takes
  the layer's `StrokeWidth` (default `1.0`), cap (SVG `butt` → `PenLineCap.Flat`) and join (default
  `Miter`).
- **Opacity**: a layer with `Opacity < 1.0` is pushed through `DrawingContext.PushOpacity`. This is why
  the control renders `Duotone` correctly and `ToGeometry` / `{ei:IconGeometry}` do not.
- A layer that is neither filled nor stroked (`fill="none"` with no stroke — a legitimate transparent
  spacer) is skipped entirely.

## `Render` never throws

Every failure inside `Render` is swallowed: a missing glyph, an unresolvable name, malformed path data,
a third-party `IIconSet` that misbehaves. The reason is the XAML previewer — a throwing render pass takes
down the preview surface for the *whole window*, not just the icon.

There is no logging. **A typo'd `IconName` is a silent blank space.** To get an error, resolve the name
outside the control:

```csharp
using Enigma.Icons;

// Fails loudly in a unit test or at startup, unlike the control.
IconGlyph glyph = myIconSet.GetGlyph("logo", "bold");   // throws IconNotFoundException on a miss
```

## Accessibility

`Icon` is **decorative by default**: `Focusable` is `false`, and its automation peer reports
`AutomationControlType.Image` while staying out of the automation *content* view. Set
`AutomationProperties.Name` when the icon carries meaning of its own and it joins the content view:

```xml
<ei:Icon Kind="WarningCircle" AutomationProperties.Name="Validation error" />
```

Never rely on an icon alone to convey state to a screen reader without naming it.

## Binding everything from a ViewModel

```xml
<ei:Icon Kind="{Binding SelectedKind}"
         Weight="{Binding SelectedWeight}"
         Size="{Binding IconSize}"
         Foreground="{Binding AccentBrush}"
         HorizontalAlignment="Center" />
```

```csharp
using Enigma.Icons.Phosphor;

public PhosphorIcon SelectedKind { get; set => SetProperty(ref field, value); } = PhosphorIcon.Star;
public PhosphorWeight SelectedWeight { get; set => SetProperty(ref field, value); } = PhosphorWeight.Regular;
public double IconSize { get; set => SetProperty(ref field, value); } = 24;
```

Note the ViewModel default of `PhosphorWeight.Regular` written **explicitly** — leaving the field at
`default` would silently be `Thin`.

Inside a `DataTemplate`, bind shared appearance up to the parent ViewModel rather than baking it into each
item, so changing it repaints the already-realized icons instead of rebuilding the list:

```xml
<DataTemplate x:DataType="vm:IconEntry">
  <ei:Icon Kind="{Binding Kind}"
           Weight="{Binding $parent[Window].((vm:MainWindowViewModel)DataContext).SelectedWeight}"
           Size="{Binding $parent[Window].((vm:MainWindowViewModel)DataContext).IconSize}"
           HorizontalAlignment="Center" />
</DataTemplate>
```

## Styling — house-wide defaults

All eight properties are `StyledProperty` and none is a `DirectProperty`, so ordinary Avalonia styling
works. This is the right way to set app-wide icon defaults, and it is not documented anywhere else:

```xml
<Style Selector="ei|Icon">
  <Setter Property="Size" Value="20" />
  <Setter Property="Weight" Value="Bold" />
</Style>

<Style Selector="ei|Icon.large">
  <Setter Property="Size" Value="32" />
</Style>
```

Trap: a `<Setter Property="IconSet" …/>` in a broad selector **blanks every `Kind`-based icon in scope**,
because a non-null `IconSet` wins unconditionally and the setter supplies no `IconName`. Scope such a
setter to a class.

`Render` ignores `FlowDirection`, so icons do **not** mirror in RTL layouts. Apply a `ScaleTransform`
yourself where direction matters.

## Using a custom set from XAML

The control is the **only** XAML route to a non-Phosphor set — the markup extensions have no `IconSet`
property.

```xml
<ei:Icon IconSet="{Binding MyIconSet}" IconName="logo" Variant="bold" Size="32" />
```

Note that `IIconSet` and `SvgIconSet` live in `Enigma.Icons`, which the `ei` URI does **not** map (it
covers only `Enigma.Icons.Avalonia` and `…Avalonia.Markup`). To name those types in XAML — for an
`x:Static` reference or direct construction — add `xmlns:eic="using:Enigma.Icons"`.

### Driving Phosphor by string name

This is also how you bind Phosphor from string data with no converter — point `IconSet` at the Phosphor
singleton and bind `IconName`:

```xml
<Window xmlns:ph="using:Enigma.Icons.Phosphor" …>
  <ei:Icon IconSet="{x:Static ph:PhosphorIconSet.Instance}"
           IconName="{Binding IconName}"
           Variant="duotone"
           Size="24" />
</Window>
```

**On this path `Variant` is live and `Weight` is dead** — the exact inverse of the `Kind` path. Setting
`Weight="Duotone"` here does nothing; you must write `Variant="duotone"`. And the variant string is
normalized far less forgivingly than an icon name: `"duotone"`, `"Duotone"`, `"DUOTONE"` and `" duotone "`
all resolve, but `"DuoTone"`, `"duo-tone"` and `"duo_tone"` are **misses**, because no weight name
contains a hyphen.

If the name comes from data, prefer converting it once in the ViewModel — that keeps the trimming-safe
typed path and fails loudly:

```csharp
using Enigma.Icons.Phosphor;

public PhosphorIcon Kind =>
    PhosphorIconNames.TryParse(_name, out PhosphorIcon icon) ? icon : PhosphorIcon.Question;
```

## Common mistakes

- **No `Kind`** → an acorn. `default(PhosphorIcon)` is enum 0, which is `Acorn`.
- **No `Foreground` and no enclosing text scope** → **black**, which on a dark theme reads as missing.
  (Invisible means an explicit null, which is a different bug.)
- **`Foreground="{StaticResource …}"`** → freezes the colour; the icon stops following a variant switch.
  Use `DynamicResource`.
- **`Weight` on the `IconSet` path** → ignored. Use `Variant`.
- **Setting `IconSet` and `Kind` expecting a fallback** → `Kind` is dead while `IconSet` is non-null.
- **`IconSet` set, `IconName` still null** → blank, not an acorn.
- **Trusting the control to report a bad name** → it never does. `Render` swallows everything, silently.
- **`Stretch="None"` without `ClipToBounds`** → a 256 DIP glyph painted over the neighbouring controls.
- **Icon in a vertical `StackPanel` with default alignment** → bounds stretch to the panel width; the
  glyph is centred in an oversized hit area, and distorts under `Stretch="Fill"`. Set
  `HorizontalAlignment`.
- **Expecting `Size` to cap the rendered size** → it sets the *desired* size; `Render` scales into
  `Bounds`. Use `Width`/`Height` for a hard size.
- **Asserting rendering in a `[Fact]`** → needs `[AvaloniaFact]` and the headless platform
  (`setup.md` §5).
