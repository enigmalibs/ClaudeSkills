# SOLID — review-standards reference

Read this when reviewing `SOLID`. The house skills still apply and are cited, not repeated: dotnet-di-design (abstractions, no `new`-ing services, no stateful statics, over-injection, lifetimes, captive dependencies, `IOptions<T>`) and csharp-extension-methods (what belongs on the class vs in an extension). Every check below is a *design* smell: severity follows the blast radius, and one occurrence in a small app is rarely more than Low.

## Single responsibility

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| God class | a class over ~400 lines, or named `Manager`, `Helper`, `Utils`, `Service` with no noun in front | Medium | split by reason to change; name each part after what it owns |
| ViewModel doing I/O | `File.`, `HttpClient`, `DbContext`, `Process.Start` inside a `*ViewModel` | High | an injected service; the ViewModel orchestrates and holds state |
| Mixed layers in one method | a method that validates, persists and formats for display | Medium | one method per step; the caller composes |
| Over-injection | 5+ constructor parameters (dotnet-di-design) | Medium | split the class, or a facade for the cohesive subset |
| Static state | `static` fields holding mutable state; `static` classes doing I/O (dotnet-di-design) | High | a registered service with a deliberate lifetime |

## Open/closed

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Type-code switches | the same `switch`/`if` chain on an enum or `is Type` repeated in 2+ places | Medium | polymorphism or a strategy per case; one chain is fine, a repeated one is not |
| Edit-to-extend | adding a case means editing a central class: a `switch` in a factory, a `Kind` enum, a `Handle(object)` | Medium | a registration point: keyed DI services, a dictionary of handlers |
| Copy-pasted variants | two classes or methods that differ by a type or a constant | Medium | one generic, parameterized implementation (dotnet-di-design) |

## Liskov substitution

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Override that refuses | `throw new NotSupportedException()` / `NotImplementedException` in an override or interface member | High | split the interface, or stop deriving |
| Tightened preconditions | an override rejects inputs the base accepts (extra `ArgumentException`s) | Medium | honour the base contract, or compose instead of inherit |
| Type checks on subclasses | `if (x is DerivedA)` in a base class or a consumer | Medium | a virtual member or a strategy |
| Empty override | `override … { }` to switch base behaviour off | Medium | a template-method hook, or composition |

## Interface segregation

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Fat interface | 8+ members, or named after the implementation (`IOrderService` with 20 methods) | Medium | split by consumer: `IOrderReader`, `IOrderWriter` |
| Partial implementation | implementers throwing or returning `null` for members they do not support | High | the interface is wrong; split it |
| One member used | a class injects a wide interface and calls one method | Low | a narrower interface, or a delegate |

## Dependency inversion

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| `new` of a collaborator | `new SomeService()`, `new HttpClient()`, `new Logger` inside a class (dotnet-di-design) | High | constructor injection |
| Service locator | `IServiceProvider` injected into a non-factory class; `GetService` in business code | High | inject the dependency; a factory or `Func<T>` for deferred creation |
| Concrete dependency | a constructor takes `SqlOrderRepository` where `IOrderRepository` exists or should | Medium | the abstraction (dotnet-di-design) |
| Lifetime mismatch | a singleton taking a scoped or transient dependency (dotnet-di-design: captive dependency) | High | `IServiceScopeFactory`, a scope per operation |
| Raw configuration | `IConfiguration["Key"]` in a service (dotnet-di-design) | Medium | an options class through `IOptions<T>` |
| Stateful extension class | a `*Extensions` class with a cache or counter (csharp-extension-methods) | Medium | a DI service |

## When not to flag

- DTOs, records, options classes and generated code: no behaviour, no SOLID.
- A small app with one implementation per interface: do not demand interfaces for everything. Flag only what blocks testing or substitution — dotnet-di-design's "could plausibly be swapped, mocked, or gain a second implementation".
- One `switch` on an enum in one place is a switch, not an open/closed breach.
