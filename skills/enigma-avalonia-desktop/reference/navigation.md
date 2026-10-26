# Navigation

`NavigationView` (a `TemplatedControl`) renders a rail of `NavigationItem`s — main list plus footer list
— and a selection. `INavigationService` owns the item collections, the current page, and a
**`PageFactory`** that turns a selected `NavigationItem` into a `Control`. Bind the view to the service
and drive everything from a ViewModel.

Pages are **never** constructed by the library. `PageFactory` is a `Func<NavigationItem, Control>` that
must return a control with its `DataContext` already set. The default factory calls
`Activator.CreateInstance` on the item's `PageType` and `PageViewModelType`, so both must be concrete
types with a public parameterless constructor — replace it to resolve from a container.

## Public API

**`NavigationView`** (`…Controls.Navigation`)

| Member | Type | Default | Notes |
|---|---|---|---|
| `Items` | `IReadOnlyList<NavigationItem>?` | `null` | Main list. |
| `FooterItems` | `IReadOnlyList<NavigationItem>?` | `null` | Pinned to the far end of the rail. |
| `SelectedItem` | `NavigationItem?` | `null` | Two-way; assigning it navigates. |
| `Logo` | `object?` | `null` | Arbitrary content at the head of the rail. |
| `Orientation` | `NavigationOrientation` | `Vertical` | `Vertical` \| `Horizontal`. |
| `PaneSize` | `double` | `90` | Cross-axis extent: the rail's `Width` when vertical, its `MaxHeight` when horizontal. |

**`NavigationItem`** (`…Controls.Navigation`) — `Header` : `string?`, `IconData` : `Geometry?`,
`PageType` : `Type`, `PageViewModelType` : `Type`, `LabelMaxWidth` : `double` (default `72`; caps the
label width in **horizontal** orientation only).

**`INavigationService`** (`…Services`)

- `ObservableCollection<NavigationItem> Items { get; }` and `FooterItems { get; }`
- `NavigationItem? SelectedItem { get; set; }` — setting it navigates
- `Control? CurrentPage { get; }`
- `Task NavigateToAsync(Control page, object? parameter = null)`
- `Func<NavigationItem, Control> PageFactory { get; set; }`
- `event EventHandler<NavigationFailedEventArgs>? NavigationFailed`

Navigation is serialized by a single `SemaphoreSlim` taken with a **zero** timeout, so a navigation
requested while one is in flight is **dropped**, not queued.

**`NavigationFailedEventArgs`** (`…Services`) — `Exception` and `Phase` (`string`).

## Page lifecycle — `INavigationViewModel`

A page's ViewModel (or the view itself) may implement `INavigationViewModel` (`…Services`):

- `Task<bool> OnDisappearingAsync()` — return **`false` to cancel** navigating away.
- `Task OnAppearingAsync(object? parameter = null)` — receives the `NavigateToAsync` parameter.

## Example — DI-resolved pages

```csharp
using System;
using Avalonia.Controls;
using Enigma.Avalonia.Desktop.Controls.Navigation;
using Enigma.Avalonia.Desktop.Services;
using Microsoft.Extensions.DependencyInjection;

public sealed class ContainerPageFactory(IServiceProvider services)
{
    public Control Create(NavigationItem item)
    {
        var page = (Control)services.GetRequiredService(item.PageType);
        page.DataContext = services.GetRequiredService(item.PageViewModelType);
        return page;
    }
}
```

```csharp
using System;
using CommunityToolkit.Mvvm.ComponentModel;
using Enigma.Avalonia.Desktop.Controls.Navigation;
using Enigma.Avalonia.Desktop.Services;
using Enigma.Icons.Avalonia;    // ToGeometry()
using Enigma.Icons.Phosphor;

public class MainWindowViewModel : ObservableObject
{
    public MainWindowViewModel(IServiceProvider services, INavigationService navigation)
    {
        Navigation = navigation;
        Navigation.PageFactory = new ContainerPageFactory(services).Create;

        Navigation.Items.Add(new NavigationItem
        {
            Header = "Home",
            IconData = PhosphorIconSet.Instance
                .GetGlyph(PhosphorIcon.House, PhosphorWeight.Regular)
                .ToGeometry(),
            PageType = typeof(HomePageView),
            PageViewModelType = typeof(HomePageViewModel)
        });

        Navigation.FooterItems.Add(new NavigationItem
        {
            Header = "Settings",
            IconData = PhosphorIconSet.Instance
                .GetGlyph(PhosphorIcon.Gear, PhosphorWeight.Regular)
                .ToGeometry(),
            PageType = typeof(SettingsPageView),
            PageViewModelType = typeof(SettingsPageViewModel)
        });

        Navigation.SelectedItem = Navigation.Items[0];   // show the first page on startup

        Navigation.NavigationFailed += (_, e) => Log(e.Phase switch
        {
            "PageFactory"        => $"The page could not be built: {e.Exception}",
            "OnAppearingAsync"   => $"The page failed while appearing: {e.Exception}",
            "OnDisappearingAsync"=> $"The page failed while leaving: {e.Exception}",
            _                    => $"Navigation failed in phase '{e.Phase}': {e.Exception}",
        });
    }

    public INavigationService Navigation { get; }
}
```

`IconData` is a plain `Geometry?` — `Geometry.Parse("M3 17…")` works just as well, and no icon pack is a
dependency of this library. The `PhosphorIconSet` calls above come from `Enigma.Icons.Avalonia`, which
you add yourself.

With a container factory, `PageType` and `PageViewModelType` act as container keys rather than
`Activator` arguments, so both halves may have constructor dependencies. Register Views transient and
ViewModels singleton so a revisited page gets a fresh control and its previous state.

## Example — horizontal rail

```xml
<nav:NavigationView Items="{Binding Navigation.Items}"
                    FooterItems="{Binding Navigation.FooterItems}"
                    SelectedItem="{Binding Navigation.SelectedItem}"
                    Orientation="Horizontal"
                    PaneSize="72" />
```

Give the items a `LabelMaxWidth="96"` when their headers are long — it only bites in horizontal
orientation.

## Example — cancelling a navigation

```csharp
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using Enigma.Avalonia.Desktop.Controls.ContentDialog;
using Enigma.Avalonia.Desktop.Services;
using Microsoft.Extensions.DependencyInjection;

public class EditorPageViewModel : ObservableObject, INavigationViewModel
{
    public async Task<bool> OnDisappearingAsync()
    {
        if (!HasUnsavedChanges) return true;

        var result = await _dialogService.ShowAsync(d =>
        {
            d.Title = "Unsaved changes";
            d.Content = "Discard your changes and leave?";
            d.PrimaryButtonText = "Discard";
            d.SecondaryButtonText = "Keep editing";
            d.DefaultButton = DefaultButton.Secondary;
        });

        return result == DialogResult.Primary;   // false ⇒ navigation cancelled
    }

    public Task OnAppearingAsync(object? parameter = null) => Task.CompletedTask;

    // Navigate to a page the rail never lists.
    private async Task GoToDetailsAsync(int id)
    {
        var page = _services.GetRequiredService<DetailsPageView>();
        page.DataContext = _services.GetRequiredService<DetailsPageViewModel>();
        await _navigation.NavigateToAsync(page, id);   // arrives as OnAppearingAsync's parameter
    }
}
```

## Notes & common mistakes

- **Nothing on `INavigationService` throws.** A page-factory or lifecycle exception is reported on
  `NavigationFailed` with a `Phase` string instead. Not subscribing means failures are invisible.
- **`PageFactory` failures clear `CurrentPage` to `null`**, so the content area empties rather than
  keeping the old page.
- **Forgetting to replace `PageFactory` when using DI** — the default `Activator.CreateInstance` cannot
  inject constructor dependencies and will throw into `NavigationFailed`.
- **A navigation requested during another is dropped**, not queued — the semaphore has a zero timeout.
  Do not fire two navigations back to back and assume both land.
- **Rail icons do not share a grid**: each item's 24×24 `PathIcon` zooms its geometry's own ink bounds,
  not the glyph's view box — pick icons with similar bounds (`SKILL.md`, *`IconData` slots drop the icon's
  view box*).
- Prefer awaiting `NavigateToAsync` from an async context over blocking with
  `.GetAwaiter().GetResult()`.
