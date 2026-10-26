# Exceptions — review-standards reference

Read this when reviewing `EXC`. The house skill still applies and is cited, not repeated: dotnet-async (`OperationCanceledException` is caught only by the level that owns the operation; no `async void` outside UI event handlers; never block on async code). `logging.md` of this skill says what to log when catching.

## Catch blocks

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Empty catch | `catch { }` / `catch (Exception) { }` with no body or only a comment | High; Critical on a write, delete, send or payment path | catch the specific type you can handle, or let it propagate |
| Catch-all swallowing | `catch (Exception ex)` that logs and returns `null`/`false`/default | High | handle only what you can; `throw;` the rest |
| `throw ex;` | rethrow with the variable (CA2200), resetting the stack | Medium | `throw;` |
| Wrap without inner | `throw new AppException("…")` inside a catch, without `ex` as inner exception | Medium | pass `ex` as `innerException` |
| Catch too wide | a `try` around 50 lines to catch one call's `IOException` | Low | narrow the `try` to the call that throws |
| Retry forever | `while (true) { try … catch { continue; } }` | High | bounded retries with backoff and a final failure |
| Catch as control flow | `try { int.Parse } catch`; `FileNotFoundException` as an existence check | Medium | `TryParse`, `File.Exists`, a result type |
| Side effects in a filter | a `when` clause that logs or mutates | Low | a filter decides; the body acts |

## Throwing

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Base exceptions thrown | `throw new Exception("…")`, `ApplicationException`, `SystemException` | Medium | a specific BCL type (`InvalidOperationException`, `ArgumentException`) or a domain exception |
| Exceptions for expected outcomes | "not found", "already exists", validation failures thrown as the normal path | Medium | a result type, `bool Try…`, or `null` for a lookup |
| Guard clauses by hand | `if (x is null) throw new ArgumentNullException(nameof(x));` | Low | `ArgumentNullException.ThrowIfNull(x)`, `ArgumentOutOfRangeException.ThrowIfNegative(…)`, `ObjectDisposedException.ThrowIf(…)` |
| Missing guards on a public API | public methods dereferencing parameters without a check | Medium | guard clauses at the public boundary only |
| Custom exception without the shape | not `: Exception`, no message/inner constructors, not `sealed`, not named `*Exception` | Low | the standard shape |

## Disposal and `finally`

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Manual `Dispose` in `finally` | `try { … } finally { x.Dispose(); }` | Low | a `using` declaration |
| `IDisposable` not disposed | a `Stream`, `HttpResponseMessage`, `DbConnection`, `CancellationTokenSource` created outside a `using` | High | `using` / `await using`; a field owner implements `IDisposable` |
| Cleanup that can throw in `finally` | `finally { Flush(); }` masking the original exception | Medium | guard the cleanup, or move it |

## Async and cancellation

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Exceptions lost | `async void` beyond UI handlers; fire-and-forget `_ = DoAsync()` with no continuation (dotnet-async) | High | return `Task`; observe the task — a continuation on fault, or a helper that logs |
| Cancellation treated as failure | `catch (Exception ex)` logging `OperationCanceledException` as an error | Medium | `catch (OperationCanceledException) when (ct.IsCancellationRequested)` at the owner, silent (dotnet-async) |
| `AggregateException` handling | code unwrapping `AggregateException` because of `.Wait()`/`.Result` | Medium | `await` (dotnet-async) |

## UI command handlers

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Unhandled command failure | an `AsyncRelayCommand` handler awaiting I/O with no `try` and no global handler | High | catch at the handler, log, show the error (`InfoBar` / `ContentDialog` in enigma-avalonia-desktop; a dialog service in WPF) |
| Crash on the user's input | a parse or I/O exception reaching the dispatcher | High | validate first; handle at the command |
| Raw `ex.Message` shown | `ShowAsync(ex.Message)` or `ex.ToString()` to the user | Low | a user-facing message; the detail goes to the log |

## Global handlers

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| No last-resort handler | none of `AppDomain.CurrentDomain.UnhandledException`, `TaskScheduler.UnobservedTaskException`, the dispatcher handler (`Dispatcher.UIThread.UnhandledException` / `DispatcherUnhandledException`) | Medium | register all three at startup: log at `Critical`, then decide to continue or exit |
| Handler that hides everything | a global handler setting `Handled = true` without logging | High | log, show once, exit when the state is unknown |
