# Ribbon

Office-style ribbon in `Enigma.Avalonia.Desktop.Controls.Ribbon`
(`xmlns:ribbon="using:Enigma.Avalonia.Desktop.Controls.Ribbon"`). Hierarchy:
`Ribbon` → `RibbonTab`s → `RibbonGroup`s → buttons.

## Public API

- **`Ribbon`** : `Tabs` : `AvaloniaList<RibbonTab>` (`[Content]`), `SelectedTab` : `RibbonTab?` (two-way),
  `SelectedIndex` : `int` (two-way, default `0`).
- **`RibbonTab`** : `Header` : `string?`, `Groups` : `AvaloniaList<RibbonGroup>` (`[Content]`).
- **`RibbonGroup`** : `Header` : `string?`, `Items` : `AvaloniaList<Control>` (`[Content]`).
- **`RibbonButton`** : `Header` : `string?`, `IconData` : `Geometry?`, `Command` : `ICommand?`,
  `CommandParameter` : `object?`.
- **`RibbonToggleButton`** : the same, plus `IsChecked` : `bool` (two-way).
- **`RibbonDropDownButton`** : `Header`, `IconData`, `IsDropDownOpen` : `bool` (two-way),
  `Items` : `AvaloniaList<RibbonMenuItem>` (`[Content]`).
- **`RibbonMenuItem`** : `Header`, `IconData`, `Command`, `CommandParameter`. Derives from
  `AvaloniaObject`, **not** `Control`.

## Example

```xml
<DockPanel>
  <ribbon:Ribbon DockPanel.Dock="Top" SelectedIndex="{Binding SelectedTabIndex, Mode=TwoWay}">
    <ribbon:RibbonTab Header="Home">
      <ribbon:RibbonGroup Header="File">
        <ribbon:RibbonButton Header="New"  IconData="{ei:IconGeometry FileText}"  Command="{Binding NewCommand}" />
        <ribbon:RibbonButton Header="Save" IconData="{ei:IconGeometry FloppyDisk}" Command="{Binding SaveCommand}" />
      </ribbon:RibbonGroup>

      <ribbon:RibbonGroup Header="Clipboard">
        <ribbon:RibbonDropDownButton Header="Paste"
                                     IconData="{ei:IconGeometry Clipboard}"
                                     IsDropDownOpen="{Binding IsPasteMenuOpen, Mode=TwoWay}">
          <ribbon:RibbonMenuItem Header="Paste"         Command="{Binding PasteCommand}" />
          <ribbon:RibbonMenuItem Header="Paste special" Command="{Binding PasteSpecialCommand}" />
        </ribbon:RibbonDropDownButton>
      </ribbon:RibbonGroup>

      <ribbon:RibbonGroup Header="Format">
        <ribbon:RibbonToggleButton Header="Bold"
                                   IconData="{ei:IconGeometry TextB}"
                                   IsChecked="{Binding IsBoldActive}"
                                   Command="{Binding ToggleBoldCommand}" />
      </ribbon:RibbonGroup>
    </ribbon:RibbonTab>

    <ribbon:RibbonTab Header="Insert">
      <ribbon:RibbonGroup Header="Elements">
        <ribbon:RibbonButton Header="Image" IconData="{ei:IconGeometry Image}" Command="{Binding InsertImageCommand}" />
      </ribbon:RibbonGroup>
    </ribbon:RibbonTab>
  </ribbon:Ribbon>

  <!-- your content fills the rest of the DockPanel -->
</DockPanel>
```

The ViewModel is plain `ObservableObject` — one `IRelayCommand` per button, plus `bool` toggle properties
and `SelectedTabIndex`:

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

public class EditorRibbonViewModel : ObservableObject
{
    public EditorRibbonViewModel()
    {
        NewCommand        = new RelayCommand(() => Status = "New");
        ToggleBoldCommand = new RelayCommand(() => Status = IsBoldActive ? "Bold on" : "Bold off");
        PasteCommand      = new RelayCommand(() => { Status = "Pasted"; IsPasteMenuOpen = false; });
    }

    public int  SelectedTabIndex  { get; set => SetProperty(ref field, value); }
    public bool IsBoldActive      { get; set => SetProperty(ref field, value); }
    public bool IsPasteMenuOpen   { get; set => SetProperty(ref field, value); }
    public string Status          { get; set => SetProperty(ref field, value); } = "Ready";

    public IRelayCommand NewCommand { get; }
    public IRelayCommand ToggleBoldCommand { get; }
    public IRelayCommand PasteCommand { get; }
}
```

## Notes

- **Buttons execute on pointer press, not release.** `RibbonButton` marks the press handled only when
  the command actually ran, so a press blocked by `CanExecute` keeps bubbling; `RibbonToggleButton` and
  `RibbonDropDownButton` always handle it.
- **`RibbonToggleButton` writes `IsChecked` before invoking `Command`**, and the property binds two-way
  by default. Read the bound state in the handler rather than flipping it — flipping there fights the
  binding.
- **Invoking a menu item does not close the drop-down**; only a light-dismiss click outside the popup
  does. Bind `IsDropDownOpen` and clear it from the command when a selection should close the menu (as
  `PasteCommand` does above).
- **`RibbonMenuItem` derives from `AvaloniaObject`, not `Control`**: it cannot go into
  `RibbonGroup.Items`, it has no template of its own — the drop-down renders it as an icon-and-label
  button — and its bindings resolve against the scope that declares it, since it has no `DataContext`.
- **`SelectedTab` is `null` until the template is applied**, at which point the first tab is selected if
  nothing else has been. Writes to `SelectedIndex` always propagate to `SelectedTab`; the reverse sync
  runs once templated. An index outside `0..Tabs.Count - 1` is ignored, and clearing `SelectedTab` sets
  `SelectedIndex` to `-1`. Removing the selected tab at runtime does **not** move the selection — assign
  one of the two properties yourself afterwards.
- **There is no collapsed or minimised state**: the tab strip and the selected tab's content are always
  visible. Dock the ribbon to the top of a `DockPanel` so it never scrolls with the content.
- **Icons are filled with the theme foreground by `PathIcon`** (24×24 on buttons, 14×14 in menus), so
  single-path monochrome geometry reads best; outline-only paths render as slivers.
- **Ribbon icons do not share a grid**: each `PathIcon` zooms its geometry's own ink bounds to the slot,
  so `TextB` (136 × 168) is drawn as tall as `FloppyDisk` (192 × 192) — pick icons with similar bounds
  (`SKILL.md`, *`IconData` slots drop the icon's view box*).

## Common mistakes

- Wrong `xmlns` — the ribbon types are under `…Controls.Ribbon`, not `…Controls`.
- Putting arbitrary controls inside a `RibbonDropDownButton` — its content is `RibbonMenuItem`s only.
- Putting a `RibbonMenuItem` in a `RibbonGroup` — it is not a `Control`.
- Flipping `IsChecked` inside a toggle's command handler — it is already written, and the binding is
  two-way.
