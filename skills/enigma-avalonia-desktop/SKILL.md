---
name: enigma-avalonia-desktop
description: Use when building or extending an Avalonia desktop app with the Enigma.Avalonia.Desktop control library (NuGet package Enigma.Avalonia.Desktop) — including adopting it into an app that does not reference it yet, or restyling standard Avalonia controls with its theme — spanning NavigationView, Ribbon, DockingHost, the typed Editors, ContentDialog, Overlay, InfoBar, SettingsCard/SettingsCardExpander, the CollectionView data subsystem, the six DI services, host/storage-provider wiring, and the Enigma* Fluent theme keys.
metadata:
  version: "3.0.3"
---

# Enigma.Avalonia.Desktop

Control library for **Avalonia 12** desktop apps (Fluent-based, Dark + Light), published on nuget.org
as `Enigma.Avalonia.Desktop` (1.0.0, 1.1.0, **1.2.0**) — repo `enigmalibs/Enigma.Avalonia`. Targets
`net8.0` and `net10.0`. **This skill documents 1.2.0**, the version dotnet-solution-config's CPM
template pins; additions since 1.0.0 are marked "since 1.1.0" / "since 1.2.0" where they are described.

Everything it ships is one of exactly two things, and the split runs through the whole API:

- **Controls** are `TemplatedControl`s (a few are `ContentControl`s) used directly in XAML, styled by
  the one theme dictionary you merge into `Application.Resources`.
- **Services** are interfaces in `Enigma.Avalonia.Desktop.Services` that you register as singletons
  and inject into ViewModels. Three of them drive a **host control** you place in the window and hand
  over once at startup (`RegisterHost`); two need the window's storage provider
  (`SetStorageProvider`). Calling a service before its wiring throws `InvalidOperationException`.

MVVM-friendly (`CommunityToolkit.Mvvm` arrives transitively) but not MVVM-bound. No ViewModel in this
library ever needs to see a `Window`.

## Install

```bash
dotnet add package Enigma.Avalonia.Desktop      # the control library
dotnet add package Avalonia.Desktop             # desktop backend/lifetime
dotnet add package Avalonia.Fonts.Inter         # WithInterFont(); the theme is designed around Inter
```

Versions come from the house CPM template (the Desktop group of dotnet-solution-config's
`Directory.Packages.props`), and the Avalonia package set is **version-coupled** — dotnet-solution-config
owns both. This package needs `Avalonia` / `Avalonia.Themes.Fluent` ≥ 12.1.1 and `CommunityToolkit.Mvvm`
≥ 8.4.2: pin anything lower and restore fails with NU1605.

**Transitively you get:** `Avalonia`, `Avalonia.Themes.Fluent`, `CommunityToolkit.Mvvm`, and
`Enigma.Core` (which brings `BouncyCastle.Cryptography`, ~4.7 MB, for the `Base64Editor` /
`HexadecimalEditor` encoding — there is no way to opt out short of not referencing the package).

**You do NOT get transitively** — add these yourself if you want them:
`Microsoft.Extensions.DependencyInjection` (or `Microsoft.Extensions.Hosting`), `Avalonia.Desktop`,
`Avalonia.Fonts.Inter`, and any icon pack.

## Bootstrap (5 steps — full detail in `reference/setup.md`)

1. **Merge the theme** in `App.axaml`: keep the base `<FluentTheme/>` in `Application.Styles`, and add
   this library's dictionary as a **`ResourceInclude` in `Application.Resources`**. It has a
   `ResourceDictionary` root, so a `StyleInclude` fails the build with `AVLN2000`:
   ```xml
   <Application.Styles><FluentTheme /></Application.Styles>
   <Application.Resources>
     <ResourceDictionary>
       <ResourceDictionary.MergedDictionaries>
         <ResourceInclude Source="avares://Enigma.Avalonia.Desktop/Themes/Fluent.axaml" />
       </ResourceDictionary.MergedDictionaries>
     </ResourceDictionary>
   </Application.Resources>
   ```
2. **Register the six services** as singletons. The library ships **no** `AddEnigmaServices()` — write
   that extension yourself; `reference/setup.md` has the block.
3. **Place the three host controls** as the last children of the window's root `Panel`
   (`ContentDialog`, `Overlay`, `InfoBar`), each `x:Name`d so they overlay everything.
4. **Hand the hosts over once** in `App.OnFrameworkInitializationCompleted`, before the window is
   shown: `RegisterHost(...)` ×3 plus `SetStorageProvider(mainWindow.StorageProvider)` ×2.
5. **Inject services** into ViewModels by constructor and call `service.ShowAsync(...)` — `await` a
   dialog (for its result) or an overlay, but not an InfoBar from a command: its task completes only
   when the bar closes (`reference/dialogs-overlay-infobar.md`).

Set the window's own `Background="{DynamicResource EnigmaBackgroundBrush}"` — the theme paints
controls, not the window.

## Quick reference

| Control / feature | XAML `xmlns` (`using:…`) | Purpose | Reference |
|---|---|---|---|
| SettingsCard, SettingsCardExpander, Overlay | `Enigma.Avalonia.Desktop.Controls` | Settings rows / modal blocking layer | `settings-cards.md`, `dialogs-overlay-infobar.md` |
| ContentDialog | `Enigma.Avalonia.Desktop.Controls.ContentDialog` | Modal dialog + `DialogResult` / `DefaultButton` | `dialogs-overlay-infobar.md` |
| InfoBar | `Enigma.Avalonia.Desktop.Controls.InfoBar` | Inline notification + `InfoBarSeverity`, optional auto-close (`DisplayDuration`) | `dialogs-overlay-infobar.md` |
| NavigationView, NavigationItem | `Enigma.Avalonia.Desktop.Controls.Navigation` | Side/top nav shell + page switching | `navigation.md` |
| Editors (Int/Double/Text/Hex/Base64/…) | `Enigma.Avalonia.Desktop.Controls.Editors` | Thirteen typed, validated input fields | `editors.md` |
| Ribbon, RibbonTab/Group/Button/… | `Enigma.Avalonia.Desktop.Controls.Ribbon` | Office-style ribbon | `ribbon.md` |
| DockingHost + the `Dock*Model` tree | `Enigma.Avalonia.Desktop.Controls.Docking` | IDE-style dockable panes | `docking.md` |
| File/Folder pickers | `Enigma.Avalonia.Desktop.Services` | `IFileDialogService` / `IFolderDialogService` | `file-folder-dialogs.md` |
| CollectionViewSource, CollectionView | `Enigma.Avalonia.Desktop.Data` | Sort / filter / group over a collection | `data-collectionview.md` |
| Theme colours & brushes | — | `Enigma*` `{DynamicResource}` keys | `theming.md` |

Note the **separate `xmlns` prefixes**: `ContentDialog`, `InfoBar`, `NavigationView` and the docking,
ribbon and editor families each live in their own CLR namespace. A single
`using:Enigma.Avalonia.Desktop.Controls` reaches only `SettingsCard`, `SettingsCardExpander` and
`Overlay`.

## Cross-cutting conventions

- **Theme brushes**: always `{DynamicResource Enigma…Brush}`, never `StaticResource` — the brushes are
  bound to theme-scoped colours, so `StaticResource` freezes the colour and the control stops
  following a variant switch. Common: `EnigmaBackgroundBrush`, `EnigmaSurfaceBrush`,
  `EnigmaForegroundSecondaryBrush`, `EnigmaBorderSubtleBrush`.
- **Icons**: every icon slot in this library is a plain `Geometry?` (`IconData`), so **any** `Geometry`
  works — including `Geometry.Parse("M3 17…")`. No icon pack is a dependency. If you want one,
  `Enigma.Icons.Avalonia` is the house pack (add it yourself):
  `xmlns:ei="https://github.com/josueclement/Enigma.Icons"`, then `{ei:IconGeometry Gear}` in an
  `IconData` slot; from C#,
  `PhosphorIconSet.Instance.GetGlyph(PhosphorIcon.Gear, PhosphorWeight.Regular).ToGeometry()`.
  `<ei:Icon Kind="Gear"/>` is for icons in your own markup — a slot cannot take it.
- **`IconData` slots drop the icon's view box.** The library paints every slot through its own
  fixed-size `PathIcon` (a uniform-stretch `Path` in a 48×48 `Viewbox` in `ContentDialog`), which zooms
  the geometry's **tight ink bounds** to the slot — a `Geometry` carries no `0 0 256 256` box. Icons with
  very different ink bounds therefore do not share an optical grid in a ribbon or a navigation rail, and
  you control neither the size nor the stretch, so the icons skill's fixed-size-`Path` workaround is not
  available. Mitigate: pick icons with similar ink bounds, and use `Regular` or `Bold` — never `Duotone`,
  which `ToGeometry` flattens so its backing layer paints solid. Details:
  [**enigma-icons-avalonia**'s `reference/markup-extensions.md`](../enigma-icons-avalonia/reference/markup-extensions.md),
  *The view box is dropped*. The real fix — `IconData` accepting `object` content, or a geometry boxed to
  256 × 256 — is a change to `Enigma.Avalonia.Desktop`, not to this skill.
- **MVVM**: `ObservableObject` / `ObservableValidator`, `RelayCommand` / `AsyncRelayCommand`, and
  semi-auto properties — `public T X { get; set => SetProperty(ref field, value); }`, with an initializer
  (`… } = string.Empty;`) or a `T?` type for a reference type, or CS9264 fails the build
  (**communitytoolkit-mvvm**).

## Gotchas that cost real time

1. **The `Enigma.Avalonia.*` ↔ `Avalonia.*` namespace collision.** Inside a namespace of your own that
   begins `Enigma.Avalonia…`, an inline reference to `Avalonia.Something` resolves against
   `Enigma.Avalonia` and fails to compile. Put `using` directives at **file scope, above the
   `namespace` declaration**, where they resolve in the global namespace; reach for
   `global::Avalonia.…` only where a using cannot express it. (Consumers under an unrelated root
   namespace never hit this.)
2. **Compiled bindings need `x:DataType`.** Compiled bindings are on by default in Avalonia 12
   (`AvaloniaUseCompiledBindingsByDefault` defaults to `true`; no csproj switch needed), so every
   `UserControl` root and every `DataTemplate` using `{Binding}` needs an explicit `x:DataType` or the
   build fails with `AVLN2100`.
3. **`{TemplateBinding}` is one-way only.** A two-way template binding must be written
   `{Binding …, RelativeSource={RelativeSource TemplatedParent}, Mode=TwoWay}`.
4. **Hit testing needs a non-null `Background`.** A control with `Background="{x:Null}"` — or none at
   all — receives no pointer events over its empty area. Set `Background="Transparent"` on areas that
   must be clickable or hoverable.

Also worth knowing: `AVLN*` XAML warnings are emitted from an MSBuild task and are **not** promoted by
`TreatWarningsAsErrors`, so a build can print `Build succeeded` while carrying XAML warnings. Read the
warning count on any project that compiles `.axaml`.

## Also use it when

- **The app does not reference the package yet.** Adopting the library is in scope —
  `reference/setup.md` covers adding the package and wiring it up, then using its controls.
- **You are styling standard Avalonia controls.** Merging the theme restyles `TextBox` and `ComboBox`
  automatically by overriding FluentTheme's own brush keys; `reference/theming.md` lists the `Enigma*`
  keys to reference from your own markup.

## When NOT to use

- Non-Avalonia UIs — WPF, WinForms, .NET MAUI, or web. This library is Avalonia-only.
- Mobile or browser targets. It is a desktop control library; the packaged assets target
  `net8.0`/`net10.0` desktop.

Read the relevant `reference/*.md` for the full public API, a runnable example, and the mistakes that
actually happen.
