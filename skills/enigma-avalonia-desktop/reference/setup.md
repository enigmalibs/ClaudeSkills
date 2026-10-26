# Setup & bootstrap

How to stand up an Avalonia desktop app that consumes `Enigma.Avalonia.Desktop`, using
`Microsoft.Extensions.Hosting` + DI. The snippets follow the library's own showcase app
(`samples/Enigma.Avalonia.Desktop.Showcase`), which is the reference wiring.

> **Retrofitting an existing app?** You still need all five pieces: the theme merge (step 4), service
> registration (step 2), the host controls in the window (step 5), and the one-time host wiring
> (step 4). If you already have an `IHost`, just add `AddEnigmaServices()` to it.

## 1. Project file

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <BuiltInComInteropSupport>true</BuiltInComInteropSupport>
    <ApplicationIcon>Assets/app.ico</ApplicationIcon>
    <!-- LangVersion / Nullable / ImplicitUsings / TreatWarningsAsErrors come from the solution's
         Directory.Build.props (dotnet-solution-config) — never repeated per project. Compiled
         bindings need no switch: AvaloniaUseCompiledBindingsByDefault is true by default in 12. -->
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Enigma.Avalonia.Desktop" />
    <PackageReference Include="Avalonia.Desktop" />
    <PackageReference Include="Avalonia.Fonts.Inter" />
    <PackageReference Include="Microsoft.Extensions.Hosting" />
  </ItemGroup>
  <ItemGroup>
    <AvaloniaResource Include="Assets/**" />
  </ItemGroup>
</Project>
```

`Avalonia`, `Avalonia.Themes.Fluent`, `CommunityToolkit.Mvvm` and `Enigma.Core` arrive transitively —
reference them explicitly only to pin a version. `Microsoft.Extensions.DependencyInjection` does **not**
arrive transitively; it comes with `Microsoft.Extensions.Hosting` above, or reference it directly if you
compose the container by hand.

The references carry no `Version`: under Central Package Management (the house default) every version
lives in `Directory.Packages.props` — dotnet-solution-config's template pins all four (Desktop and App
hosting groups), and owns the version-coupled-ecosystem rule the Avalonia packages follow. **Without** CPM,
and only then, add each version inline, copied from that template.

## 2. DI registration

The library ships **no** registration extension — write this one yourself. All six services are
singletons: three own a host control registered once at startup, two own the window's storage provider,
and the navigation service owns the rail's items and the current page. C# 14 extension members are used
here; a plain static method works identically.

```csharp
using Enigma.Avalonia.Desktop.Services;
using Microsoft.Extensions.DependencyInjection;

public static class ServiceCollectionExtensions
{
    extension(IServiceCollection services)
    {
        public void AddEnigmaServices()
        {
            services.AddSingleton<INavigationService, NavigationService>();
            services.AddSingleton<IContentDialogService, ContentDialogService>();
            services.AddSingleton<IOverlayService, OverlayService>();
            services.AddSingleton<IInfoBarService, InfoBarService>();
            services.AddSingleton<IFileDialogService, FileDialogService>();
            services.AddSingleton<IFolderDialogService, FolderDialogService>();
        }
    }
}
```

Register your window, page Views and ViewModels alongside. The showcase's split is deliberate:
**Views transient, ViewModels singleton** — navigating back to a page builds a fresh `Control` but
re-attaches the ViewModel it had before, so page state survives leaving it while the visual tree does
not leak.

```csharp
using Microsoft.Extensions.DependencyInjection;

services.AddSingleton<MainWindow>();
services.AddTransient<HomePageView>();          // fresh Control per navigation
services.AddSingleton<HomePageViewModel>();     // state survives navigation
services.AddSingleton<MainWindowViewModel>();
```

## 3. `Program.cs`

```csharp
using System;
using Avalonia;

namespace MyApp;

public static class Program
{
    [STAThread]
    public static void Main(string[] args)
        => BuildAvaloniaApp().StartWithClassicDesktopLifetime(args);

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>().UsePlatformDetect().WithInterFont().LogToTrace();
}
```

This is the **avalonia** skill's `Program.cs` without `.WithDeveloperTools()`, which needs the
`AvaloniaUI.DiagnosticsSupport` package this project file does not reference.

The host is built in `App.OnFrameworkInitializationCompleted` (step 4), not here — that keeps the
composition root next to the wiring that consumes it and means the Avalonia designer, which bypasses
`Program.Main`, never sees a half-initialised static.

## 4. `App.axaml` + `App.axaml.cs`

`App.axaml` — base `FluentTheme` in `Styles`, this library's dictionary as a `ResourceInclude` in
`Resources`:

```xml
<Application xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Class="MyApp.App"
             RequestedThemeVariant="Dark">
  <Application.Styles>
    <FluentTheme />
  </Application.Styles>
  <Application.Resources>
    <ResourceDictionary>
      <ResourceDictionary.MergedDictionaries>
        <ResourceInclude Source="avares://Enigma.Avalonia.Desktop/Themes/Fluent.axaml" />
      </ResourceDictionary.MergedDictionaries>
    </ResourceDictionary>
  </Application.Resources>
</Application>
```

`RequestedThemeVariant` sets the starting variant (`Dark` or `Light`); omit it and Avalonia follows the
OS. Keep `<FluentTheme />` — this library declares a `ControlTheme` only for its own controls, so
dropping it leaves every framework control, including the ones nested inside these templates, without a
template.

`App.axaml.cs` — build the host, resolve the window, and **register the host controls once**. It is
the **avalonia** skill's `App.axaml.cs` plus the Enigma lines: the services using, the two
registration calls (`AddPagesAndViewModels()` is yours — it registers the window, the pages and their
ViewModels as in step 2), and the five handovers.

```csharp
using System;
using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using Enigma.Avalonia.Desktop.Services;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using MyApp.ViewModels;
using MyApp.Views;

namespace MyApp;

public partial class App : Application
{
    private IHost? _host;

    public override void Initialize() => AvaloniaXamlLoader.Load(this);

    public override void OnFrameworkInitializationCompleted()
    {
        // A desktop app must not depend on the working directory, so config is read beside the executable.
        HostApplicationBuilder builder = Host.CreateApplicationBuilder(new HostApplicationBuilderSettings
        {
            ContentRootPath = AppContext.BaseDirectory,
        });
        builder.Services.AddEnigmaServices();
        builder.Services.AddPagesAndViewModels();

        IHost host = builder.Build();
        host.Start();
        _host = host;

        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            IServiceProvider services = host.Services;
            MainWindow mainWindow = services.GetRequiredService<MainWindow>();
            mainWindow.DataContext = services.GetRequiredService<MainWindowViewModel>();

            // All five run before the window is handed over: a service whose host is still
            // unregistered throws the moment a page asks it for a dialog, an overlay or a picker.
            services.GetRequiredService<IContentDialogService>().RegisterHost(mainWindow.HostDialog);
            services.GetRequiredService<IOverlayService>().RegisterHost(mainWindow.HostOverlay);
            services.GetRequiredService<IInfoBarService>().RegisterHost(mainWindow.HostInfoBar);
            services.GetRequiredService<IFileDialogService>().SetStorageProvider(mainWindow.StorageProvider);
            services.GetRequiredService<IFolderDialogService>().SetStorageProvider(mainWindow.StorageProvider);

            desktop.MainWindow = mainWindow;
            desktop.Exit += (_, _) =>
            {
                host.StopAsync().GetAwaiter().GetResult();
                host.Dispose();
            };
        }

        base.OnFrameworkInitializationCompleted();
    }
}
```

The host is **started, never run** — Avalonia's classic desktop lifetime runs the application; the host
only supplies configuration, logging and services.

## 5. MainWindow — the host `Panel` pattern

The three host controls are the **last** children of a root `Panel` (which z-stacks its children), so
they overlay everything the app draws. The `x:Name`s must match what `App.axaml.cs` passes to
`RegisterHost`.

```xml
<Window xmlns="https://github.com/avaloniaui"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:vm="using:MyApp.ViewModels"
        xmlns:controls="using:Enigma.Avalonia.Desktop.Controls"
        xmlns:contentDialog="using:Enigma.Avalonia.Desktop.Controls.ContentDialog"
        xmlns:infoBar="using:Enigma.Avalonia.Desktop.Controls.InfoBar"
        xmlns:nav="using:Enigma.Avalonia.Desktop.Controls.Navigation"
        x:Class="MyApp.Views.MainWindow"
        x:DataType="vm:MainWindowViewModel"
        Icon="/Assets/app.ico"
        Background="{DynamicResource EnigmaBackgroundBrush}">
  <Panel>
    <DockPanel>
      <nav:NavigationView DockPanel.Dock="Left"
                          Items="{Binding Navigation.Items}"
                          FooterItems="{Binding Navigation.FooterItems}"
                          SelectedItem="{Binding Navigation.SelectedItem}"
                          Orientation="Vertical"
                          PaneSize="90" />
      <ContentControl Content="{Binding Navigation.CurrentPage}" />
    </DockPanel>

    <contentDialog:ContentDialog x:Name="HostDialog" />
    <controls:Overlay x:Name="HostOverlay" />
    <infoBar:InfoBar x:Name="HostInfoBar" />
  </Panel>
</Window>
```

Each `x:Name`d host becomes a field on the generated `MainWindow` partial class — that is why
`App.axaml.cs` can pass `mainWindow.HostDialog` / `HostOverlay` / `HostInfoBar` to `RegisterHost`. You
do not declare those fields yourself.

Note the **four separate `xmlns` prefixes**: `ContentDialog`, `InfoBar` and `NavigationView` live in
different CLR namespaces, and a lone `using:Enigma.Avalonia.Desktop.Controls` resolves only
`SettingsCard`, `SettingsCardExpander` and `Overlay`.

## Common mistakes

- **`StyleInclude` for the theme** → build failure `AVLN2000`: the URI resolves to a
  `Avalonia.Controls.ResourceDictionary` where `Avalonia.Styling.IStyle` was expected. Use
  `ResourceInclude` inside `Application.Resources`.
- **Dropping `<FluentTheme />`** → every framework control loses its template, including those nested
  inside this library's own templates.
- **Merging your own overrides before `Fluent.axaml`** → silently ignored. On a duplicate key the last
  dictionary wins, so an override of an `Enigma*` key must be merged **after**.
- **Calling a service before `RegisterHost` / `SetStorageProvider`** → `InvalidOperationException`. Wire
  all five at startup, before the window is shown.
- **Expecting the theme to paint the window** → it does not. Set
  `Background="{DynamicResource EnigmaBackgroundBrush}"` on the `Window` yourself.
- **Wrong package id** — it is `Enigma.Avalonia.Desktop` (with dots).
- **Forgetting `Avalonia.Desktop` / `Avalonia.Fonts.Inter`** — the library does not bring them; without
  them `StartWithClassicDesktopLifetime` / `WithInterFont()` will not resolve.
- **Expecting an `AddEnigmaServices()` from the package** — there is none. Write it (step 2).
