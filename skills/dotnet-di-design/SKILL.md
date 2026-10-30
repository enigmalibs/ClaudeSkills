---
name: dotnet-di-design
description: Use when designing or refactoring C# classes and services — constructor dependencies, static vs injected helpers, choosing service lifetimes, or registering services with Microsoft.Extensions.DependencyInjection.
metadata:
  version: "1.0.1"
---

# Reusable, DI-friendly class design

- Depend on **abstractions**: when a dependency could plausibly be swapped, mocked, or gain a second implementation, take an interface through the constructor.
- **No `new`-ing services inside services** — loggers, clocks, HTTP clients, repositories all arrive via constructor injection.
- No `static` classes or singletons for anything that holds state, performs I/O, or must be substituted in tests — register it in the container with a deliberate lifetime instead. Pure stateless helpers (e.g. extension-method classes, see csharp-extension-methods) may stay static.
- Single responsibility per class. Over-injection (a constructor asking for 5+ services) is a smell — split the class. ViewModels and services request only what they use.
- Prefer one generic, parameterized implementation over copy-pasted variants.
- Configuration binds through `IOptions<T>` / `IOptionsMonitor<T>`; services never take raw `IConfiguration`.

## Lifetimes

| Lifetime | Use for | Examples |
|---|---|---|
| `Singleton` | Stateless or thread-safe app-wide services; state that lives as long as the app | `IClock`, caches, the shell/root ViewModel, the main window |
| `Scoped` | Per-request / per-unit-of-work state | repositories, `DbContext` |
| `Transient` | Cheap, short-lived, per-consumer instances | dialog ViewModels, validators |

**ViewModels take the lifetime of their state.** The shell/root ViewModel and the main window are `Singleton` — one per app lifetime. A dialog ViewModel is `Transient`, a fresh instance per dialog. A navigation page's ViewModel is `Singleton` when the page keeps its state across navigation (the Enigma.Avalonia.Desktop pattern: View transient, ViewModel singleton), otherwise `Transient`. A singleton obtains a transient ViewModel through a factory or the navigation service, never through its constructor.

Never inject a `Scoped`/`Transient` service into a `Singleton` (captive dependency) — inject `IServiceScopeFactory` and create a scope per operation instead.

## Registration

```csharp
builder.Services.AddSingleton<IClock, SystemClock>();
builder.Services.AddScoped<IInvoiceRepository, SqlInvoiceRepository>();
builder.Services.AddSingleton<MainWindowViewModel>();      // shell/root ViewModel
builder.Services.AddTransient<ConfirmDeleteViewModel>();   // dialog ViewModel
builder.Services.AddOptions<SmtpOptions>().BindConfiguration("Smtp");
```

Host/bootstrapping conventions: see dotnet-solution-setup. As everywhere: every file declares its own `using` directives — no implicit usings.

## Common mistakes

| Mistake | Fix |
|---|---|
| `new HttpClient()` / `new Logger(...)` inside a service | Constructor-inject (`IHttpClientFactory`, `ILogger<T>`) |
| `static class AppState { public static User Current; }` | A registered service with a deliberate lifetime |
| Service reads `IConfiguration["Smtp:Host"]` | Bind `SmtpOptions`, inject `IOptions<SmtpOptions>` |
| Singleton constructor taking a `Scoped` service | `IServiceScopeFactory` + scope per operation |

If an existing codebase diverges (service locator, stateful statics), stay consistent where you must and flag the divergence rather than silently mixing styles.
