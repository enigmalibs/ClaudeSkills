---
name: avalonia
description: Use when creating or modifying an Avalonia application — project setup and packages, bootstrapping and DI/IHost wiring, XAML bindings, views and ViewModels, or desktop app lifetime.
metadata:
  version: "2.0.1"
---

# Avalonia 12 conventions

House rule: new Avalonia work targets **Avalonia 12** — never start new work on 11. Apps target `net10.0` (Avalonia 12 requires .NET 8+). MVVM uses CommunityToolkit.Mvvm per the communitytoolkit-mvvm skill — not ReactiveUI.

## Packages (12.x template set)

Versions come from the CPM template — the Desktop group of dotnet-solution-config's `Directory.Packages.props`, the one place the Avalonia version is pinned — so the project references carry none:

```xml
<PackageReference Include="Avalonia" />
<PackageReference Include="Avalonia.Desktop" />
<PackageReference Include="Avalonia.Themes.Fluent" />
<PackageReference Include="Avalonia.Fonts.Inter" />
<!-- Dev tools: Avalonia.Diagnostics was REMOVED in 12 -->
<PackageReference Include="AvaloniaUI.DiagnosticsSupport">
  <IncludeAssets Condition="'$(Configuration)' != 'Debug'">None</IncludeAssets>
  <PrivateAssets Condition="'$(Configuration)' != 'Debug'">All</PrivateAssets>
</PackageReference>
```

**Without** CPM, and only then, each reference takes its version inline (`Version="…"`), copied from that template. The Avalonia packages are a version-coupled set — dotnet-solution-config owns the rule.

General csproj properties (LangVersion 14, nullable, no implicit usings): see dotnet-solution-setup.

## Bootstrapping — Avalonia lifetime + IHost

`await host.RunAsync()` alone never shows a window; keep `Main` synchronous and run Avalonia's classic desktop lifetime:

```csharp
// Program.cs
using System;
using Avalonia;

namespace MyApp;

public static class Program
{
    [STAThread]
    public static void Main(string[] args) => BuildAvaloniaApp()
        .StartWithClassicDesktopLifetime(args);

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
#if DEBUG
            .WithDeveloperTools()   // 12: replaces window-level this.AttachDevTools()
#endif
            .WithInterFont()
            .LogToTrace();
}
```

```csharp
// App.axaml.cs
using System;
using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
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
        builder.Services.AddSingleton<MainWindow>();
        builder.Services.AddSingleton<MainWindowViewModel>();
        // options, logging, hosted services …

        IHost host = builder.Build();
        host.Start();
        _host = host;

        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            IServiceProvider services = host.Services;
            MainWindow mainWindow = services.GetRequiredService<MainWindow>();
            mainWindow.DataContext = services.GetRequiredService<MainWindowViewModel>();

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

The host is built in `OnFrameworkInitializationCompleted`, not in `Main`: the composition root sits next to the wiring that consumes it, and the Avalonia designer, which bypasses `Program.Main`, never sees a half-initialised static. It is **started, never run** — the classic desktop lifetime runs the app; the host only supplies configuration, logging and services, and is stopped and disposed when that lifetime exits.

- Resolve the main window and root ViewModels/services from `host.Services` — never `new` them; keep XAML code-behind free of service instantiation.
- Long-running background work: `IHostedService`/`BackgroundService` on the builder; marshal UI updates via `Dispatcher.UIThread` (see dotnet-async).

## Application icon

Ship one multi-resolution `.ico` under `Assets/` (16/32/48/256 px in a single file, so the taskbar icon isn't blurry) and wire it **two ways** — the built executable and the running window are separate concerns:

```xml
<!-- .csproj: embeds the icon in the Windows .exe; Windows-only — no effect on the Linux/macOS binary -->
<PropertyGroup>
  <ApplicationIcon>Assets/app.ico</ApplicationIcon>
</PropertyGroup>
<ItemGroup>
  <AvaloniaResource Include="Assets/**" />
</ItemGroup>
```

```xml
<!-- MainWindow.axaml: runtime titlebar/taskbar icon on every platform — and the only one that does anything on Linux/macOS -->
<Window ... Icon="/Assets/app.ico">
```

One `.ico`, referenced from both places: `<ApplicationIcon>` gives the `.exe` its icon (Explorer/taskbar show it even when the app isn't running), `Icon="/Assets/app.ico"` covers the running window everywhere. The `.ico` art is user-owned; `git-repo-hygiene` already marks `*.ico binary`.

## Compiled bindings (default ON in 12)

- Plain `{Binding}` compiles; the **root of every view and every `DataTemplate` needs `x:DataType`** or the build fails: `x:DataType="vm:MainWindowViewModel"`.
- Per-binding escape hatch for dynamic shapes: `{ReflectionBinding Path}`; scope opt-out: `x:CompileBindings="False"`.
- The template ViewLocator (`IDataTemplate` mapping `FooViewModel` → `FooView`) is still the pattern for VM-first navigation; register it in `<Application.DataTemplates>`.

## Common v11-isms to avoid (all wrong in 12)

| v11 habit | Avalonia 12 |
|---|---|
| `Avalonia.Diagnostics` package + `this.AttachDevTools()` | `AvaloniaUI.DiagnosticsSupport` + `.WithDeveloperTools()` |
| `BindingPlugins.DataValidators.RemoveAt(0)` in App | Obsolete — data-annotations validation is off by default |
| `Avalonia.ReactiveUI` package | Renamed `ReactiveUI.Avalonia` (but house MVVM is CommunityToolkit) |
| Assuming compiled bindings are off / sprinkling `x:CompileBindings="True"` | On by default; just provide `x:DataType` |
| `SystemDecorations`, `ExtendClientAreaChromeHints`, `Clipboard.GetTextAsync()`, `DoDragDrop()` | Removed/renamed (`WindowDecorations`, `TryGetTextAsync()`, `DoDragDropAsync`) |
| Targeting net6.0/net7.0 | Minimum net8.0 — use `net10.0` |

When scaffolding, surface the OS targets (Windows/Linux/macOS) and packaging/deployment decisions — see the checklist in dotnet-solution-setup.

If an existing app is on Avalonia 11, stay consistent with it and flag the divergence — upgrading to 12 is its own work item.
