---
name: wpf
description: Use when creating or modifying a WPF application — project setup, entry point and App.xaml wiring, IHost/DI integration, or resolving windows and ViewModels at startup.
---

# WPF conventions

## Project setup

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net10.0-windows</TargetFramework>
    <UseWPF>true</UseWPF>
    <!-- LangVersion / Nullable / ImplicitUsings / TreatWarningsAsErrors come from the solution's
         Directory.Build.props (dotnet-solution-config) — never repeated per project. -->
  </PropertyGroup>
</Project>
```

Solution layout, TFM policy, and general IHost conventions: see dotnet-solution-setup.

## Bootstrapping — IHost + WPF lifetime

Build a `Microsoft.Extensions.Hosting` `IHost` like every other app, but **run WPF's own lifetime** — `await host.RunAsync()` alone never shows a window. WPF generates the `[STAThread]` `Main` from `App.xaml`; the host lives in `App`:

```csharp
using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

public partial class App : Application
{
    private readonly IHost _host;

    public App()
    {
        HostApplicationBuilder builder = Host.CreateApplicationBuilder();
        builder.Services.AddSingleton<MainViewModel>();
        builder.Services.AddSingleton<MainWindow>();
        _host = builder.Build();
    }

    protected override void OnStartup(StartupEventArgs e)
    {
        _host.Start();
        MainWindow window = _host.Services.GetRequiredService<MainWindow>();
        window.Show();
        base.OnStartup(e);
    }

    protected override void OnExit(ExitEventArgs e)
    {
        // Blocking is safe here: the dispatcher loop has already exited.
        _host.StopAsync().GetAwaiter().GetResult();
        _host.Dispose();
        base.OnExit(e);
    }
}
```

- Resolve the root types (main window, root ViewModel) from `host.Services` in `OnStartup` — never `new` them up.
- Keep XAML code-behind free of service instantiation; anything a view needs comes through its ViewModel.
- Long-running background work: `IHostedService`/`BackgroundService` registered on the builder, not `Task.Run`.

## Related conventions

- ViewModels, observable properties, commands: communitytoolkit-mvvm (no source generators).
- Dispatcher marshaling from background threads: dotnet-async.
- Extension helpers: csharp-extension-methods.

If an existing WPF codebase has its own bootstrapping (e.g. no IHost), stay consistent and flag the divergence rather than mixing patterns.
