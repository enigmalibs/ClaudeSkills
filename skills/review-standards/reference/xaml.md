# XAML — review-standards reference

Read this when reviewing `XAML` (`.axaml`, `.xaml`). The house skills still apply and are cited, not repeated: avalonia (compiled bindings and `x:DataType`, the ViewLocator, no service instantiation in code-behind, v11-isms), wpf (code-behind free of services), enigma-avalonia-desktop (`DynamicResource` for theme brushes, `x:DataType` on templates, `{TemplateBinding}` is one-way, hit testing needs a `Background`, `AVLN*` warnings are not promoted to errors) and enigma-icons-avalonia when icons are involved. The baseline's `AVLN*` warning count feeds this dimension.

## Redundancy

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Repeated setter groups | the same 3+ attributes (`Margin`, `Padding`, `FontSize`, `Foreground`, …) on 3+ elements of one type | Medium | a `Style` with a selector (Avalonia) or an implicit or keyed style (WPF), in the view's or the app's resources |
| Duplicated templates | two `DataTemplate`s or `ControlTemplate`s that differ by a binding path or a colour | Medium | one template with a binding or a `DynamicResource`; a `ContentControl` for the variable part |
| Copy-pasted views | two views sharing most of their markup | Medium | a `UserControl` with styled properties, or a template over a shared ViewModel base |
| Inline styles everywhere | `<Control.Styles>` inside many elements for the same selector | Low | hoist to the view root or the app |
| Converter proliferation | several converters that each do one `bool → something` | Low | a ViewModel property exposing the display value; one generic converter with a parameter |

## Resources

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Hard-coded colours | `#RRGGBB`, `Red`, `White` in element attributes | Medium | a brush resource; theme brushes through `DynamicResource` (enigma-avalonia-desktop) |
| Magic spacing | the same `Margin="0,8,0,0"` / `Spacing="12"` literal repeated | Low | a `Thickness`/`Double` resource |
| `StaticResource` on a theme brush | `{StaticResource Enigma…Brush}`, or any brush that changes with the theme | Medium | `DynamicResource` (enigma-avalonia-desktop *Cross-cutting conventions*) |
| Unused resources | a key in `<Resources>` that `grep -r "Resource Key}"` never finds | Low | delete |
| Unused namespaces | an `xmlns:` prefix never used in the file | Low | delete |

## Code-behind

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Logic in code-behind | `.axaml.cs`/`.xaml.cs` handlers that compute, validate or call services | High | a command or ViewModel property; code-behind only for view-only concerns (focus, scroll, animation) |
| Service instantiation or resolution in a view | `new Service()`, `App.Services.GetService` in a view (avalonia, wpf) | High | the ViewModel takes it by constructor |
| `x:Name` only for code-behind reads | elements named so code-behind can read `.Text` or `.IsChecked` | Medium | bind to the ViewModel |
| Visual tree walking | `FindControl`, `GetVisualDescendants`, `Parent.Parent` in handlers | Medium | bindings, or a behavior |

## Bindings

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Missing `x:DataType` | a view root or `DataTemplate` with `{Binding}` and no `x:DataType` (avalonia; enigma-avalonia-desktop gotcha 2) | High | add it; `x:CompileBindings="False"` only with a reason |
| `ReflectionBinding` without reason | `{ReflectionBinding}` where the type is known | Low | `{Binding}` with `x:DataType` |
| View as its own DataContext | `DataContext="{Binding $self}"`, or a view exposing properties for its own markup | Medium | a ViewModel |
| Two-way where one-way | `Mode=TwoWay` on read-only display | Low | `OneWay`; `OneWayToSource` where it is only input |
| Collection replaced per refresh | a ViewModel assigning a new `ObservableCollection` on every load | Medium | mutate the collection, or expose a `CollectionView` (enigma-avalonia-desktop `data-collectionview.md`) |

## Layout

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Nested panels reducible to one | `StackPanel` in `StackPanel` in `Grid` to align two things | Low | one `Grid` with rows and columns, or a `DockPanel` |
| Fixed pixel sizes on text | `Width`/`Height` on a `TextBlock` or a `Button` containing text | Low | `MinWidth`, or let the content size it |
| Misaligned repeated rows | label/field rows in separate grids whose columns drift | Low | `SharedSizeGroup`, or one grid |
| Hidden by `Opacity` | `Opacity="0"` on something still hit-testable | Low | `IsVisible="False"` |

## Avalonia vs WPF

- `IsVisible` (Avalonia) vs `Visibility` (WPF); `Classes` and selectors (Avalonia) vs `Style.Triggers` (WPF); `Spacing` on `StackPanel` is Avalonia-only.
- A WPF-ism in Avalonia markup (`Visibility="Collapsed"`, a `Style` with `TargetType` and no selector) is Medium when it compiles by accident, High when it silently does nothing.
