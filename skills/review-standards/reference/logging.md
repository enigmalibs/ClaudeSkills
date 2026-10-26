# Logging — review-standards reference

Read this when reviewing `LOG`. The house skills still apply and are cited, not repeated: dotnet-di-design (`ILogger<T>` arrives by constructor, never `new`-ed) and dotnet-solution-setup (logging is wired through the `IHost`). A solution with no logging at all is one Medium finding ("no diagnostics"), not one per class.

## Obtaining a logger

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Logger not injected | `new LoggerFactory`, `LoggerFactory.Create` in a service, a static `Log` class, `Serilog.Log.Logger` used directly | High | `ILogger<T>` by constructor (dotnet-di-design) |
| Wrong category | `ILogger<Foo>` injected into `Bar`; a non-generic `ILogger` everywhere | Low | `ILogger<Bar>` |
| `Console.WriteLine` / `Debug.WriteLine` / `Trace.WriteLine` in production code | grep outside a CLI's `Program.Main` | Medium | the logger |

## Message templates

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Interpolated message | `_logger.LogInformation($"Order {id} saved")` (CA2254) | Medium | a template: `LogInformation("Order {OrderId} saved", id)` — properties survive structured sinks |
| Non-constant template | a template built with `+` or `string.Format` | Medium | a constant template with placeholders |
| Placeholder names | positional `{0}`, lower-case `{id}` | Low | `PascalCase` names: `{OrderId}` |
| Objects dumped | `{Order}` with a whole entity; `JsonSerializer.Serialize(x)` in a message | Medium | the few identifying properties; `@` destructuring only where the sink supports it |

## Levels

| Level | Use for |
|---|---|
| `Trace` | per-item internals; off in production |
| `Debug` | state useful to a developer following one operation |
| `Information` | one line per completed unit of work or state change a user would recognise |
| `Warning` | something unexpected the app recovered from; no action needed now |
| `Error` | an operation failed; someone should look |
| `Critical` | the app cannot continue, or data is at risk |

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Level inflation | `LogError` for a validation failure the user caused; `LogWarning` on a normal branch | Low | per the table above |
| Level deflation | `LogInformation`/`LogDebug` with an exception argument, or on a failed save | Medium | `LogError`, with the exception |
| `Information` per item | a log per element of a collection at `Information` | Medium | `Debug`/`Trace` per item, one `Information` summary |

## Exceptions in logs

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Exception not passed | `LogError("failed: " + ex.Message)`, `{Error}", ex.Message` | Medium | `LogError(ex, "…")` — the exception is the first argument; the stack survives |
| Log and throw | `catch (Exception ex) { _logger.LogError(ex, …); throw; }` at a level that does not own the operation | Medium | log once, where the exception is handled; rethrow silently below (`exceptions.md`) |
| Double logging | the same exception logged at two levels of the call chain | Medium | log where it is handled |

## Hot paths and cost

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Eager formatting | `LogDebug(ExpensiveToString())` evaluated whether or not `Debug` is enabled | Low | an `IsEnabled(LogLevel.Debug)` guard, or the `LoggerMessage` source generator |
| Logging per render or tick | a log call in a draw, layout, property setter or timer tick | Medium | remove, or `Trace` behind `IsEnabled` |
| `LoggerMessage` absent on a hot path | a high-frequency `LogInformation` with 3+ arguments | Low | a `[LoggerMessage]` partial method |

## Sensitive data

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Secrets logged | tokens, passwords, connection strings, API keys as template arguments | Critical | never; log the key name or a hash prefix |
| PII logged | e-mail, full name, address, document contents at `Information` or above | High | an identifier, or `Debug` with a documented reason (`security.md`) |
| Payloads logged | full file contents or request bodies in messages | Medium | size and identifier only |

## Boundaries

- Log at the boundary that owns the operation: a command handler, a hosted service's loop, a request pipeline. Inner services throw or return results; they rarely need to log.
- Every `BackgroundService` loop logs its start, each failure (with the exception) and its stop — a silent loop that dies is one High finding.
- Startup logs the effective configuration once at `Information`, never a secret.
