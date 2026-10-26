# SettingsCard & SettingsCardExpander

Two `TemplatedControl`s in `Enigma.Avalonia.Desktop.Controls`
(`xmlns:controls="using:Enigma.Avalonia.Desktop.Controls"`). Use them to build a settings page out of
labelled rows: an icon, a header and a description, with either an inline control, a click command, or
expandable content.

## SettingsCard

`Header` : `string?`, `Description` : `string?`, `IconData` : `Geometry?`, `Content` : `object?`
(the `[Content]` property), `Command` : `ICommand?`, `CommandParameter` : `object?`.

**Two modes, selected by `Content` alone:**

- **Content mode** — put a control inside; it renders at the trailing end of the row.
- **Command mode** — leave `Content` empty and set `Command`; the whole card becomes clickable.

## SettingsCardExpander

`Header`, `Description`, `IconData`, `Content` (the `[Content]` property), plus `IsExpanded` : `bool`
(default `false`). The content shows and hides on expand. Also useful as a plain section container with
`IsExpanded="True"`.

## Example

```xml
<UserControl xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:controls="using:Enigma.Avalonia.Desktop.Controls"
             xmlns:ei="https://github.com/josueclement/Enigma.Icons"
             xmlns:vm="using:MyApp.ViewModels"
             x:Class="MyApp.Views.SettingsPageView"
             x:DataType="vm:SettingsPageViewModel">
  <ScrollViewer>
    <StackPanel Margin="24" Spacing="16">

      <!-- Content mode: inline control -->
      <controls:SettingsCard Header="Theme"
                             Description="Switch between light and dark mode"
                             IconData="{ei:IconGeometry Moon}">
        <ToggleSwitch IsChecked="{Binding IsDarkTheme, Mode=TwoWay}"
                      OnContent="Dark" OffContent="Light" />
      </controls:SettingsCard>

      <!-- Command mode: the whole card is clickable -->
      <controls:SettingsCard Header="Appearance"
                             Description="Change theme, colours and display options"
                             IconData="{ei:IconGeometry Palette}"
                             Command="{Binding CardClickedCommand}"
                             CommandParameter="Appearance" />

      <!-- Expander with arbitrary content -->
      <controls:SettingsCardExpander Header="Preferences"
                                     Description="Configure display and behaviour options"
                                     IconData="{ei:IconGeometry Gear}">
        <StackPanel Spacing="12">
          <TextBox PlaceholderText="Display name" />
          <CheckBox Content="Enable notifications" />
        </StackPanel>
      </controls:SettingsCardExpander>

    </StackPanel>
  </ScrollViewer>
</UserControl>
```

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

public class SettingsPageViewModel : ObservableObject
{
    public SettingsPageViewModel()
        => CardClickedCommand = new RelayCommand<string?>(CardClicked);

    public bool IsDarkTheme { get; set { if (SetProperty(ref field, value)) ApplyTheme(value); } }

    public IRelayCommand CardClickedCommand { get; }

    public string? LastAction { get; private set => SetProperty(ref field, value); }

    private void CardClicked(string? key) => LastAction = $"Clicked: {key}";
}
```

## Notes

- **`Content` is the only switch between the two modes.** Setting it adds the `:hasContent`
  pseudo-class, which hides the chevron and suppresses the hover highlight, and `Command` is then never
  invoked — setting both is a silent no-op on the command. If you need a click target alongside other
  content, put a `Button` in the content.
- **A card with neither `Content` nor `Command` still shows a chevron and still highlights on hover**: it
  looks actionable and does nothing. Give every chevron row a command.
- **`CanExecute` is consulted at the moment of the press and never re-queried.** The card does not
  disable or grey itself when the command cannot run — the press is simply ignored. Bind `IsEnabled` on
  the card when that state has to be visible.
- **Both controls act on `PointerPressed`, not on click**, so there is no press-and-drag-off to cancel:
  the command fires, or the expander toggles, the instant the pointer goes down.
- **Restyling hooks** — `SettingsCard` exposes `PART_Root`, `PART_ContentPresenter` and `PART_Chevron`
  with the `:hasContent` and `:pressed` pseudo-classes; `SettingsCardExpander` exposes `PART_Root`,
  `PART_Header`, `PART_Separator`, `PART_Content` and `PART_Chevron` with `:expanded` and `:pressed`.
  Every colour resolves from an `Enigma*` brush as a `DynamicResource`, so a card follows a
  theme-variant switch without being rebuilt.

## Common mistakes

- **Setting both `Content` and `Command`** → the command never fires.
- **`IconData` given a string** → it expects a `Geometry`. Use `{ei:IconGeometry …}` or
  `Geometry.Parse(...)`.
- **Expecting a disabled look from `CanExecute`** → bind `IsEnabled` instead.
