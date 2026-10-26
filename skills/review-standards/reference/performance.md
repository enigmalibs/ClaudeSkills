# Performance — review-standards reference

Read this when reviewing `PERF`. The house skill still applies and is cited, not repeated: dotnet-async (no blocking on async code, `ConfigureAwait(false)` in libraries only, `ValueTask` only with a measured reason, UI-thread marshaling). Only obvious, local costs are findings — no profiling, no speculation: a check fires when the pattern sits on a path that runs per item, per keystroke, per render or per request, or over data that can be large. Elsewhere it is at most Low.

## Blocking and threads

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Sync over async | `.Result`, `.Wait()`, `GetAwaiter().GetResult()` outside a process edge (dotnet-async) | High | `await` all the way |
| Async over sync | `Task.Run(() => File.ReadAllText(…))` to fake asynchrony in a library | Medium | the true async API (`File.ReadAllTextAsync`), or leave it synchronous |
| I/O on the UI thread | file, network or database I/O in a command handler without `await`; heavy work in a property getter | High | `await` the I/O; compute off-thread with `Task.Run` and marshal back (dotnet-async) |
| Overlapping timers | a `System.Timers.Timer` / `DispatcherTimer` whose tick does async work with no re-entrancy guard | Medium | a `PeriodicTimer` loop, or a guard |

## Allocations and strings

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| String concatenation in loops | `s += …` / `string.Concat` per iteration | Medium | `StringBuilder`, `string.Join` |
| Formatting per call on hot paths | `ToString()` in a bound property getter; boxing through `object` parameters | Low | cache, or a typed overload |
| LINQ on hot paths | `.Where().Select().ToList()` per render, per keystroke, per item | Medium | a loop, or compute once and cache |
| Repeated materialisation | the same query `ToList()`/`ToArray()`-ed several times in one method | Low | materialise once |
| Regex per call | `Regex.IsMatch(input, pattern)` or `new Regex` inside a frequently called method | Medium | a `static readonly Regex`, or `[GeneratedRegex]` |
| Large buffers per operation | `new byte[1024 * 1024]` per call | Medium | `ArrayPool<T>`, a reusable buffer |

## Collections

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| `ObservableCollection` bulk mutation | `Clear()` then `Add` in a loop on a bound collection | Medium | a range-capable collection, or one assignment when the view tolerates it (`xaml.md`) |
| Quadratic lookups | `list.Contains` / `First(x => x.Id == id)` inside a loop over another list | Medium | a `Dictionary`/`HashSet` keyed lookup |
| `Count()` to test emptiness | `.Count() > 0`, `.Count() == 0` on an `IEnumerable` | Low | `.Any()`, or `Count` on a known collection |
| Unbounded caches | a dictionary that only grows; a static list of everything ever seen | High | `MemoryCache` with a size limit or expiry; eviction |
| Wrong collection | `List.Remove` in loops, `List.Insert(0, …)`, a `List` used as a queue | Low | `Queue`, `LinkedList`, `HashSet`, as the usage says |

## I/O and data access

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| N+1 queries | a query inside a loop over another query's result | High | one query with a join or `Include`, or a batch |
| Whole file in memory | `File.ReadAllBytes`/`ReadAllText` on files that can be large; `ReadToEnd` on streams | Medium | stream it |
| `HttpClient` per call | `new HttpClient()` in a method (dotnet-di-design: `IHttpClientFactory`) | High | `IHttpClientFactory` |
| Unindexed scans | EF or Dapper queries filtering on an unindexed column of a table that can be large | Low | an index, noted as a schema follow-up |
| Chatty disposal | a connection or stream opened and closed per item | Medium | one per unit of work |

## Startup and UI

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Work in constructors | ViewModel or service constructors doing I/O or heavy computation | Medium | a `LoadAsync` called on activation, or a hosted service |
| Everything eager at startup | all services resolved and all data loaded before the first window shows | Medium | lazy by navigation; load behind the shell |
| Unvirtualised lists | an `ItemsControl` with a `StackPanel` host showing hundreds of items | Medium | `ListBox`/`ItemsRepeater` with virtualization |
| Computed getters bound | a bound property that recomputes (LINQ, string building) on every `PropertyChanged` | Medium | cache the value; raise only when its inputs change |
