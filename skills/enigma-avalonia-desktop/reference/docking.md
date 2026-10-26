# Docking

IDE-style dockable panes in `Enigma.Avalonia.Desktop.Controls.Docking`
(`xmlns:docking="using:Enigma.Avalonia.Desktop.Controls.Docking"`). The easiest path is
**declarative**: build a `DockLayoutNode` model tree in the ViewModel and bind it to
`DockingHost.LayoutRoot`.

## Public API

**Layout model POCOs** (plain classes, not controls) — bind **these** to `LayoutRoot`:

| Type | Members |
|---|---|
| `DockLayoutNode` | Abstract base; no members of its own. |
| `DockPaneModel` | `Header` : `string`, `Content` : `object?`, `CanClose` : `bool` (`true`), `CanMove` : `bool` (`true`) |
| `DockTabGroupModel` | `Panes` : `AvaloniaList<DockPaneModel>`, `SelectedPane` : `DockPaneModel?` |
| `DockSplitModel` | `Orientation` (default `Horizontal`), `First` / `Second` : `DockLayoutNode?`, `FirstSize` / `SecondSize` : `GridLength` (default `1*`) |

**Controls** — the host, plus the three the host builds the live tree from:

| Owner | Member | Type | Default | Notes |
|---|---|---|---|---|
| `DockingHost` | `Panes` | `AvaloniaList<DockPane>` | empty | XAML content property. Read only when `LayoutRoot` is null and no root has been set. |
| `DockingHost` | `LayoutRoot` | `DockLayoutNode?` | `null` | Styled property; assigning it rebuilds the whole tree. |
| `DockingHost` | `SetRootLayout(Control)` | `void` | — | Replaces the tree with a control you built. Throws `InvalidOperationException` before the template is applied. |
| `DockingHost` | `ClosePane(DockPane)` | `void` | — | Finds the pane's group, removes it, collapses the group if it empties. |
| `DockPane` | `Header` | `string?` | `null` | Tab label. |
| `DockPane` | `PaneContent` | `object?` | `null` | XAML content property — **not** `Content`. |
| `DockPane` | `CanClose` | `bool` | `true` | `false` hides the tab's close button. |
| `DockPane` | `CanMove` | `bool` | `true` | `false` refuses to start a drag. |
| `DockTabGroup` | `Panes` | `AvaloniaList<DockPane>` | empty | **Not** a content property — use property-element syntax in XAML. |
| `DockTabGroup` | `SelectedPane` | `DockPane?` | first pane, on template applied | Two-way by default. |
| `DockTabGroup` | `PaneDragStarted`, `PaneCloseRequested` | `EventHandler<DockTabGroupEventArgs>` | — | Drag raised once a 5 px threshold is crossed. |
| `DockSplitContainer` | `First` / `Second` | `Control?` | `null` | Two children separated by a `GridSplitter`. |
| `DockSplitContainer` | `Orientation`, `FirstSize`, `SecondSize` | `Orientation`, `GridLength` | `Horizontal`, `1*` | |

**`DockTabGroupEventArgs`** — `Pane` : `DockPane`, `SourceGroup` : `DockTabGroup`, `Pointer` :
`IPointer?`.
**`DockPosition`** enum — `Center`, `Left`, `Right`, `Top`, `Bottom`.

`DockPaneModel.Content` is typically a ViewModel; provide a `DataTemplate` for its type so the pane
renders your view.

## Example

```xml
<UserControl xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:docking="using:Enigma.Avalonia.Desktop.Controls.Docking"
             xmlns:vm="using:MyApp.ViewModels"
             x:Class="MyApp.Views.WorkspaceView"
             x:DataType="vm:WorkspaceViewModel">
  <UserControl.DataTemplates>
    <DataTemplate DataType="vm:PaneContentViewModel">
      <Border Padding="16">
        <TextBlock Text="{Binding Title}" FontSize="18" FontWeight="SemiBold" />
      </Border>
    </DataTemplate>
  </UserControl.DataTemplates>

  <docking:DockingHost LayoutRoot="{Binding RootLayout}" />
</UserControl>
```

```csharp
using Avalonia.Controls;   // GridLength, GridUnitType
using Avalonia.Layout;     // Orientation
using CommunityToolkit.Mvvm.ComponentModel;
using Enigma.Avalonia.Desktop.Controls.Docking;

public class WorkspaceViewModel : ObservableObject
{
    public DockLayoutNode RootLayout { get; }

    public WorkspaceViewModel()
    {
        var solution = Pane("Solution", canClose: false, canMove: false);
        var doc1 = Pane("Doc1");
        var doc2 = Pane("Doc2");
        var output = Pane("Output");
        var debug = Pane("Debug");

        var center = new DockTabGroupModel { SelectedPane = doc1 };
        center.Panes.Add(doc1);
        center.Panes.Add(doc2);

        var solutionGroup = new DockTabGroupModel { SelectedPane = solution };
        solutionGroup.Panes.Add(solution);

        var bottom = new DockTabGroupModel { SelectedPane = output };
        bottom.Panes.Add(output);
        bottom.Panes.Add(debug);

        var top = new DockSplitModel
        {
            Orientation = Orientation.Horizontal,
            First = solutionGroup,
            Second = center,
            FirstSize = new GridLength(200, GridUnitType.Pixel),
            SecondSize = new GridLength(1, GridUnitType.Star),
        };

        RootLayout = new DockSplitModel
        {
            Orientation = Orientation.Vertical,
            First = top,
            Second = bottom,
            FirstSize = new GridLength(1, GridUnitType.Star),
            SecondSize = new GridLength(200, GridUnitType.Pixel),
        };
    }

    private static DockPaneModel Pane(string header, bool canClose = true, bool canMove = true) =>
        new()
        {
            Header = header,
            CanClose = canClose,
            CanMove = canMove,
            Content = new PaneContentViewModel { Title = header },
        };
}

public class PaneContentViewModel : ObservableObject
{
    public string Title { get; set => SetProperty(ref field, value); } = "";
}
```

## Notes

- **No layout persistence API and no floating windows.** To save a layout, serialise your own
  representation and rebuild a `DockLayoutNode` tree on startup — the live control tree is never
  projected back. `GridLength` is not JSON-friendly, so persist a number plus a unit and reconstruct
  with `new GridLength(value, GridUnitType.Star)`.
- **The live tree must consist solely of `DockSplitContainer`, `DockTabGroup` and `DockPane`.**
  Hit-testing, event wiring and empty-group collapse traverse `DockSplitContainer.First` / `Second`
  only, so a group wrapped in a `Border` or `Grid` is invisible to the docking machinery — its tabs
  still render, but drops and closes are ignored.
- **`DockingHost.Panes` is consulted once**, when the template is applied; adding to it later has no
  effect. Collapsing a group discards the sizes of the split it removes — the surviving sibling inherits
  the slot, not the proportions — and a directional drop always splits 50/50.
- **`CanClose` and `CanMove` govern user gestures only.** `ClosePane` closes a pane whose `CanClose` is
  `false`, and `SetRootLayout` places a pane whose `CanMove` is `false`. Closing drops the pane: nothing
  retains it and there is no reopen surface, so keep a reference to any `DockPane` you intend to bring
  back and rebuild the tree with it.
- **A `DockTabGroup` works outside a host** — it renders its tabs and raises both events — but nothing
  re-docks, and removing the pane is left to you. Move `SelectedPane` off it first, so the tab strip
  never points at a pane the collection no longer holds.
- **A `DockTabGroup` presents `SelectedPane.PaneContent`, not the `DockPane` control.** The pane is only
  ever data for the tab strip; that keeps it out of two logical trees at once while dragged, and it is
  why a non-`Control` content object needs a `DataTemplate`.
- **The drop overlay's colours are baked into the `DockingHost` template**, not exposed as resources.
  Changing them means supplying your own `ControlTheme` for `DockingHost`.

## Common mistakes

- **Forgetting a `DataTemplate` for the pane content type** → the pane shows the ViewModel's
  `ToString()`.
- **Calling `SetRootLayout` before the template is applied** → `InvalidOperationException`. Prefer
  binding `LayoutRoot`.
- **Confusing the model POCOs (`Dock*Model`) with the controls** (`DockPane`, `DockTabGroup`,
  `DockSplitContainer`) — bind the **models** to `LayoutRoot`.
- **Setting `Content` on a `DockPane`** → the property is `PaneContent`.
- **Using content syntax for `DockTabGroup.Panes`** → it is not a content property; use
  `<docking:DockTabGroup.Panes>`.
