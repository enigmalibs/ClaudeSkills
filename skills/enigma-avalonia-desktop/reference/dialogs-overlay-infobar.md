# ContentDialog, Overlay & InfoBar (host services)

Three service + host-control pairs sharing one pattern:

1. Place the host control (`ContentDialog` / `Overlay` / `InfoBar`) as one of the **last** children of
   MainWindow's root `Panel`, `x:Name`d (see `setup.md`).
2. `RegisterHost(...)` it once at startup in `App.OnFrameworkInitializationCompleted`, **before the
   window is shown**.
3. Inject the service into a ViewModel and `await service.ShowAsync(...)`.

This wiring is the whole contract. A service whose host is still unregistered throws
`InvalidOperationException` from every `Show*` call — `"ContentDialog host has not been registered. Call
RegisterHost first."`, `"No Overlay registered. Call RegisterHost first."`, `"InfoBar host has not been
registered. Call RegisterHost first."`. All three `HideAsync` methods are silent no-ops instead, because
there is nothing to hide. Calling `RegisterHost` twice is allowed — the last host wins.

The three controls derive from `ContentControl`, not `TemplatedControl`.

---

## ContentDialog — modal dialog

**`IContentDialogService`** (`…Services`)

| Member | Returns |
|---|---|
| `RegisterHost(ContentDialog dialog)` | `void` |
| `ShowMessageAsync(string title, string message, string closeButtonText = "OK")` | `Task<DialogResult>` |
| `ShowAsync(Action<ContentDialog> configure)` | `Task<DialogResult>` |
| `HideAsync()` | `Task` — resolves the pending dialog with `DialogResult.None` |

**`ContentDialog`** (`…Controls.ContentDialog`) — set these inside `configure`:

- `Title` : `string?`, `Content` : `object?` (inherited from `ContentControl` — a string or any control)
- `PrimaryButtonText` / `SecondaryButtonText` / `CloseButtonText` : `string?`, each with a matching
  `…ButtonCommand` : `ICommand?` and `Is…ButtonEnabled` : `bool`
- `DefaultButton` : `DefaultButton` (default `None`) — declares intent only
- `IconData` : `Geometry?`, `IconBrush` : `IBrush?`
- `IsOpen` : `bool`, `OverlayBrush` : `IBrush?` (default `#4D000000` — the scrim; clicking it closes with
  `DialogResult.None`), `DialogResult` : `DialogResult` (set to the closing button just before `Closed`
  fires)
- **Six size properties**: `DialogWidth` / `DialogHeight` (default `double.NaN` — auto-size within the
  bounds), `DialogMinWidth` / `DialogMaxWidth` (`320` / `600`), `DialogMinHeight` / `DialogMaxHeight`
  (`0` / `double.PositiveInfinity` — set the max to make tall content scroll inside the card)
- Also on the control itself: `Task<DialogResult> ShowAsync()`, `Task HideAsync()`, and
  `event EventHandler<DialogResult>? Closed`

**Enums** (`…Controls.ContentDialog`): `DialogResult { None, Primary, Secondary, Close }` and
`DefaultButton { None, Primary, Secondary, Close }`.

The size properties are **not** reset between dialogs, so set them on the host in XAML rather than in
every `configure`:

```xml
<contentDialog:ContentDialog x:Name="HostDialog"
                             DialogMinWidth="360"
                             DialogMaxWidth="900"
                             DialogMaxHeight="520" />
```

For a **Yes/No confirmation**, set `PrimaryButtonText = "Yes"` and `CloseButtonText = "No"`, then treat
**only `DialogResult.Primary`** as confirmed — dismissing with `Escape` or a scrim click returns `None`,
not `Close`, so `== DialogResult.Primary` is the only correct check.

```csharp
using Avalonia.Controls;
using Avalonia.Media;
using Enigma.Avalonia.Desktop.Controls.ContentDialog;
using Enigma.Icons.Avalonia;    // ToGeometry() — Enigma.Icons.Avalonia is a package you add yourself
using Enigma.Icons.Phosphor;

// Simple confirmation
var result = await _dialogService.ShowAsync(dialog =>
{
    dialog.Title = "Delete file";
    dialog.Content = "This cannot be undone.";
    dialog.PrimaryButtonText = "Delete";
    dialog.CloseButtonText = "Cancel";
});
if (result == DialogResult.Primary) { /* … */ }

// Rich content, three buttons, a coloured icon
await _dialogService.ShowAsync(dialog =>
{
    dialog.Title = "Confirm action";
    dialog.IconData = PhosphorIconSet.Instance
        .GetGlyph(PhosphorIcon.Warning, PhosphorWeight.Regular).ToGeometry();
    dialog.IconBrush = new SolidColorBrush(Color.Parse("#E8A33D"));
    dialog.Content = new StackPanel
    {
        Spacing = 8,
        Children = { new TextBlock { Text = "Are you sure?", TextWrapping = TextWrapping.Wrap } }
    };
    dialog.PrimaryButtonText = "Confirm";
    dialog.SecondaryButtonText = "Maybe later";
    dialog.CloseButtonText = "Cancel";
});

// One-liner message
await _dialogService.ShowMessageAsync("Done", "The export finished.");
```

Capture input by putting a control in `Content` and reading it after the await:

```csharp
using Avalonia.Controls;
using Enigma.Avalonia.Desktop.Controls.ContentDialog;

var box = new TextBox { PasswordChar = '•' };
var result = await _dialogService.ShowAsync(d => { d.Title = "Password"; d.Content = box;
                                                   d.PrimaryButtonText = "OK"; });
if (result == DialogResult.Primary) Use(box.Text);
```

`ShowAsync` resets the host's content and button configuration before applying your `configure`, so only
set what you need — but remember the size properties are excluded from that reset.

**Secondary background** (since 1.1.0). `Classes="secondary"` on the host paints the dialog card with
`EnigmaDialogSecondaryBackgroundBrush` — the window-background tone, darker than the default
`EnigmaSurfaceHighBrush` in the Dark variant — for content laid out for the window's own background. The
card (template part `PART_Card`) paints `ContentDialog.Background`, which the theme sets to
`EnigmaSurfaceHighBrush`, so a `Background` of your own applies too. Like the size properties, the look is
a host setting: `ShowAsync` resets neither `Background` nor the host's classes.

```xml
<contentDialog:ContentDialog x:Name="HostDialog" Classes="secondary" />
```

---

## Overlay — modal blocking layer

**`IOverlayService`** (`…Services`): `void RegisterHost(Overlay presenter)`,
`Task ShowAsync(Control control)`, `Task HideAsync()`.

**`Overlay`** (`…Controls`) — `IsOpen` : `bool`, `OverlayBrush` : `IBrush?` (translucent black by
default). `ShowAsync` takes any `Control` as content, typically a small progress card you build and then
mutate while a task runs.

```csharp
var card = new ProgressOverlayCard { Title = "Processing", IsIndeterminate = true, Message = "Starting…" };
await _overlayService.ShowAsync(card);
try
{
    card.IsIndeterminate = false;
    card.Progress = 50;
    card.Message = "Halfway…";
    await DoWorkAsync();
}
finally
{
    await _overlayService.HideAsync();   // always, or the overlay stays stuck open
}
```

`ProgressOverlayCard` is **your** control, not the library's — the showcase's version is a
`ContentControl` subclass exposing `Title`, `Message`, `IsIndeterminate`, `Progress`, `Minimum` and
`Maximum` styled properties over a templated `ProgressBar`. Guard the triggering command with an
`IsBusy` flag and `NotifyCanExecuteChanged()` to prevent re-entry.

---

## InfoBar — inline notification

**`IInfoBarService`** (`…Services`): `void RegisterHost(InfoBar infoBar)`,
`Task ShowAsync(Action<InfoBar>? configure = null)`, `Task HideAsync()`. Since 1.1.0,
`InfoBarServiceExtensions` (same namespace) adds `Task ShowAsync(TimeSpan displayDuration,
Action<InfoBar>? configure = null)`, which shows a bar that closes itself. The duration is applied after
`configure`, so the argument wins; an invalid one throws `ArgumentOutOfRangeException` before the host is
touched.

**`InfoBar`** (`…Controls.InfoBar`) — `Title` : `string?`, `Message` : `string?`, `Severity` :
`InfoBarSeverity`, `IsOpen` : `bool`, `DisplayDuration` : `TimeSpan?`. **Enum**:
`InfoBarSeverity { Info, Success, Warning, Error }`; each severity resolves its own
`Enigma*Background` / `Enigma*Border` brush pair.

`DisplayDuration` (since 1.1.0) defaults to `null`: the bar stays open until it is dismissed. Set, the
bar closes itself once the period has elapsed, exactly as `Close()` would — `IsOpen` goes `false`,
`Closed` is raised and the pending `ShowAsync()` completes. The countdown starts when the bar opens,
restarts when the duration changes or `ShowAsync()` is called on the open bar, and is cancelled when the
bar closes any other way. A value must be `null`, or greater than zero and at most `int.MaxValue`
milliseconds; anything else throws `ArgumentException` where it is set. `InfoBarService.ShowAsync` resets
it between messages, so a timed message never makes the next one timed.

```csharp
using Enigma.Avalonia.Desktop.Controls.InfoBar;

await _infoBarService.ShowAsync(bar =>
{
    bar.Title = "Success";
    bar.Message = "The operation completed successfully.";
    bar.Severity = InfoBarSeverity.Success;
});
// later: await _infoBarService.HideAsync();
```

A bar that closes itself after five seconds:

```csharp
using System;
using Enigma.Avalonia.Desktop.Controls.InfoBar;
using Enigma.Avalonia.Desktop.Services;   // InfoBarServiceExtensions — the TimeSpan overload

await _infoBarService.ShowAsync(TimeSpan.FromSeconds(5), bar =>
{
    bar.Message = "Saved.";
    bar.Severity = InfoBarSeverity.Success;
});
```

---

## Injecting the services

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using Enigma.Avalonia.Desktop.Services;

public class MyPageViewModel(
    IContentDialogService dialogService,
    IOverlayService overlayService,
    IInfoBarService infoBarService) : ObservableObject
{
    private readonly IContentDialogService _dialogService = dialogService;
    private readonly IOverlayService _overlayService = overlayService;
    private readonly IInfoBarService _infoBarService = infoBarService;
}
```

## Common mistakes

- **`ShowAsync` before `RegisterHost`** → `InvalidOperationException`. Wire all three hosts at startup.
- **Treating a dismissal as `Close`** → `Escape` and scrim clicks yield `DialogResult.None`. Check for
  `Primary`.
- **Setting the six size properties inside `configure`** → they are not reset between dialogs, so set
  them once on the host in XAML.
- **Not wrapping overlay work in `try`/`finally`** → an exception mid-task leaves the overlay open and
  the app unusable.
- **Missing `using Enigma.Avalonia.Desktop.Controls.ContentDialog;`** → `DialogResult` and
  `DefaultButton` are invisible; likewise `…Controls.InfoBar;` for `InfoBarSeverity`.
- **Placing the hosts before the app content in the `Panel`** → they render underneath it. They must be
  the last children.
