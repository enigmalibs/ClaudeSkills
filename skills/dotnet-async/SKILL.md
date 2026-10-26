---
name: dotnet-async
description: Use when writing async C# — Task-returning APIs, cancellation handling, background work in hosted apps, or updating UI-bound state from background threads.
---

# Async & cancellation conventions

## CancellationToken

- Every public async API accepts a `CancellationToken` as its **last parameter** (`CancellationToken cancellationToken = default`) and **propagates it** to every awaited call that takes one — never drop it mid-chain.
- Long-running loops call `cancellationToken.ThrowIfCancellationRequested()` per iteration.
- Catch `OperationCanceledException` only at the level that owns the operation, to turn cancellation into a graceful stop — never swallow it deeper down.

```csharp
public async Task<IReadOnlyList<Order>> LoadOrdersAsync(CustomerId id, CancellationToken cancellationToken = default)
{
    using HttpResponseMessage response = await _client.GetAsync(BuildUri(id), cancellationToken);
    response.EnsureSuccessStatusCode();
    return await ParseOrdersAsync(response.Content, cancellationToken);
}
```

## General rules

- Async methods end in `Async`. No `async void` — the only exception is UI framework event handlers/overrides, which delegate immediately to a private `Task`-returning method.
- Never block on async code (`.Result`, `.Wait()`, `.GetAwaiter().GetResult()`) — deadlock risk on UI/synchronization contexts. Only acceptable at process edges where no message pump remains (e.g. WPF `OnExit`).
- **Libraries** (reusable packages, `netstandard2.0` targets): `ConfigureAwait(false)` on every await. **Application code** (hosts, ViewModels, UI handlers): omit it — it needs its context.
- Default to `Task`/`Task<T>`; use `ValueTask` only with a measured reason.
- Background work in hosted apps is a `BackgroundService` honoring its `stoppingToken` — never ad-hoc `Task.Run` from `Main` or a constructor (see dotnet-solution-setup).

## UI-thread marshaling

Treat UI-bound state (properties raising `PropertyChanged`, `ObservableCollection`) as UI-thread-only. From background code, marshal:

- Avalonia: `await Dispatcher.UIThread.InvokeAsync(() => Items.Add(item));` — fire-and-forget: `Dispatcher.UIThread.Post(...)`
- WPF: `await Application.Current.Dispatcher.InvokeAsync(...)`

`AsyncRelayCommand` handlers resume on the UI thread after `await` (no `ConfigureAwait` in app code), so mutations there are safe; marshal only from genuinely background code (`BackgroundService`, `Task.Run`, callbacks on worker threads).

## Common mistakes

| Mistake | Fix |
|---|---|
| Public async API without a token parameter | Add `CancellationToken cancellationToken = default`, pass it down |
| `async void` helper method | Return `Task`; async void only for UI event handlers |
| `.Result` / `.Wait()` to bridge sync code | Make the caller async |
| `ConfigureAwait(false)` in ViewModels/app code | Only libraries use it |
| `ObservableCollection` mutated from `Task.Run` | Marshal via the dispatcher |

If an existing codebase has its own established async policy, stay consistent and flag the divergence.
