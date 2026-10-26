# Theming

One public XAML entry point: the compiled resource dictionary at
`avares://Enigma.Avalonia.Desktop/Themes/Fluent.axaml`. It merges three layers in order — `Color`
values defined once per theme variant (`Themes/Colors.axaml`), a `SolidColorBrush` per colour
(`Themes/Brushes.axaml`), and a `ControlTheme` per control the library ships. Merging that one URI is
the whole setup.

## Rules

- It is a `ResourceDictionary`, so it goes into `Application.Resources` →
  `ResourceDictionary.MergedDictionaries` as a **`ResourceInclude`**. A `StyleInclude` fails the build
  with `AVLN2000`.
- Reference **brushes**, not colours, and always with `{DynamicResource Enigma…Brush}` — never
  `StaticResource`. The colours are theme-scoped and the brushes are not: there is one brush instance
  per key whose `Color` follows the active variant through a `DynamicResource`. `StaticResource` freezes
  the colour and the control stops following a variant switch.
- Switch variant at runtime by assigning `Application.Current.RequestedThemeVariant`
  (`ThemeVariant.Dark` / `ThemeVariant.Light`, from `Avalonia.Styling`). Every control on screen
  re-colours in one step — no reload, no rebuilt visual tree.
- **Order matters inside `MergedDictionaries`.** On a duplicate key the last dictionary wins, so your
  own dictionary overriding an `Enigma*` key must be merged **after** `Fluent.axaml`. Merged before, it
  is silently ignored. (`Application.Styles` and `Application.Resources` are independent collections;
  their relative order in the file is irrelevant.)
- **The window background is yours.** The theme paints controls, not the window — set
  `Background="{DynamicResource EnigmaBackgroundBrush}"` on it or it keeps Avalonia's default.

## Key catalog

`Colors.axaml` defines **31** colour keys (1.2.0), once under `x:Key="Dark"` and once under `x:Key="Light"`
inside `ResourceDictionary.ThemeDictionaries`. `Brushes.axaml` turns **28** of them into brushes. Both
variants define the same key set — a key present in one variant only would resolve to nothing after a
switch.

Every brush key is its colour key with `Color` replaced by `Brush`
(`EnigmaSurfaceColor` → `EnigmaSurfaceBrush`), **except** the three input-background colours, which have
no `Enigma*` brush of their own and feed the FluentTheme override keys instead.

- **Surfaces** — `EnigmaBackground` (window, ribbon body, dock tab strips), `EnigmaSurface` (settings
  cards, navigation pane, editor bodies), `EnigmaSurfaceHigh` (dialog body, hovered editor),
  `EnigmaSurfaceLow` (focused editor, expanded card content)
- **Borders** — `EnigmaBorder` (dialog frame, hovered card, flyout), `EnigmaBorderSubtle` (default 1 px
  border and separator on cards, panes, groups, editors, splitters)
- **Foreground** — `EnigmaForeground` (primary text, icons, caret), `EnigmaForegroundSecondary`
  (descriptions, captions, inactive tab labels, editor titles), `EnigmaForegroundTertiary` (placeholder
  and watermark text, ribbon group labels)
- **Accent & selection** — `EnigmaAccent` (focus ring, checked-state border; deliberately the same blue
  `#3574F0` in both variants), `EnigmaAccentHover`, `EnigmaSelection` (selected nav item, checked ribbon
  toggle, text selection)
- **Interaction** — `EnigmaHover`, `EnigmaPressed`, `EnigmaOverlay` (modal scrim; the alpha channel is
  meaningful — `#80000000` Dark, `#40000000` Light)
- **Status accents** — `EnigmaSuccess`, `EnigmaWarning`, `EnigmaError`. Only `EnigmaError` is consumed
  by a shipped template (editor validation border and message); the other two are there for your own
  content.
- **Status surfaces** — `EnigmaInfoBackground` / `EnigmaInfoBorder`, and the same
  `…Background` / `…Border` pair for `EnigmaSuccess`, `EnigmaWarning`, `EnigmaError`. These are the
  `InfoBar` severity fills. Since 1.2.0 the Dark fills are pastel tints that stand out from the panels
  around them (the Light variant is unchanged); to keep the 1.1 look, override the eight keys with the
  1.1.0 Dark values listed in the package's release notes, in a dictionary merged after `Fluent.axaml`.
- **Component keys** — `EnigmaDialogSecondaryBackground` (since 1.1.0: the card of a `ContentDialog` with
  `Classes="secondary"`, the window-background tone) and `EnigmaInfoBarMessageForeground` (since 1.2.0:
  the `InfoBar` message line — the primary text tone in Dark, the secondary tone in Light).
- **Colour-only, no brush** — `EnigmaInputBackgroundColor`, `EnigmaInputBackgroundFocusedColor`,
  `EnigmaInputBackgroundHoverColor`. They exist to feed the framework `TextBox` / `ComboBox` overrides
  below; there is no `EnigmaInputBackgroundBrush` to reference.

There are **no** calendar, chart or 2D-canvas keys — the library ships no such control.

## Standard Avalonia controls

The dictionary restyles exactly two framework controls — `TextBox` and `ComboBox` — and does it by
overriding FluentTheme's own brush keys rather than replacing its templates. Those names are
FluentTheme's contract, so they appear verbatim: **13** keys for `TextBox` (`TextControlBackground`,
`TextControlBackgroundFocused`, `TextControlBackgroundPointerOver`, `TextControlBorderBrush*`,
`TextControlForeground*`, `TextControlPlaceholderForeground*`, `TextControlSelectionHighlightColor`) and
**10** for `ComboBox` (`ComboBoxBackground*`, `ComboBoxBorderBrush*`, `ComboBoxForeground*`,
`ComboBoxPlaceholderTextForeground`). Each resolves an `Enigma*` colour, which is why they follow a
variant switch like everything else.

Every other standard control keeps its FluentTheme look. You do not style `TextBox` or `ComboBox`
yourself.

## Example

```xml
<Border Background="{DynamicResource EnigmaSurfaceBrush}"
        BorderBrush="{DynamicResource EnigmaBorderSubtleBrush}"
        BorderThickness="1" CornerRadius="8" Padding="16">
  <TextBlock Text="Hello"
             Foreground="{DynamicResource EnigmaForegroundSecondaryBrush}" />
</Border>
```

Toggle the whole app theme from a ViewModel:

```csharp
using Avalonia;
using Avalonia.Styling;

Application.Current!.RequestedThemeVariant = isDark ? ThemeVariant.Dark : ThemeVariant.Light;
```

## Common mistakes

- **`StaticResource`** → the colour freezes at load and will not follow a theme switch.
- **Hard-coded hex** instead of the `Enigma*` brushes → inconsistent look and no theme reactivity.
- **Referencing `EnigmaInputBackgroundBrush`** → it does not exist. Those three are colour keys only.
- **Merging an override dictionary before `Fluent.axaml`** → silently ignored.
- **Restyling `TextBox` by hand** → unnecessary, and it fights the FluentTheme key overrides. Override
  the `TextControl*` keys after `Fluent.axaml` instead.
