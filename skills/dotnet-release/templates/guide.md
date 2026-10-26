<!--
  Per-category guide template. Copy into the target repo as docs/guides/<category>.md — one guide
  per category the library actually has (one category, one guide; the count follows the library).
  Create only if missing — diff against an existing guide, never clobber it.

  Placeholders: none — a guide is written for its category. <Angle-bracket> text marks what to
  replace. Expect roughly 100–300 lines depending on the category's surface.

  Two non-negotiables:
    1. EVERY snippet must compile against the REAL public API. There is no compile harness for doc
       snippets, so the verification gate is what catches drift: cross-check every using, type,
       factory method, member, argument shape, enum and extension against src/ before the guide
       ships, and record the coverage table in the completion doc.
    2. EVERY snippet carries its FULL using block — including System — so it is genuinely
       copy-pasteable, not a fragment the reader has to repair.

  This file lives under docs/ and is never packed, so relative links are correct here.
-->
# <Category>

<!-- Intro: 2–3 short paragraphs.
     (1) what this category does;
     (2) the idiom for reaching it — the concrete types, in order;
     (3) the one cross-cutting property that matters, stated as a consequence for the caller
         ("all X is stream-based and asynchronous, so processing a multi-gigabyte file uses the
         same constant memory as processing a short string"). -->
<Library> provides <what this category does> through <the idiom — factory, service, helper>. You
create a `<ConcreteFactory>`, ask it for the <thing> you need, and get back an `<IService>` that
<does the operation> over <the input type>.

<The one cross-cutting property that matters here, and what it means for the caller.>

## Supported <algorithms/schemes/operations>

| <Algorithm> | <Factory method> | Notes |
|-------------|------------------|-------|
| <Name> | `<CreateXService>` | Legacy / broken. Interop only — never for security. |
| <Name> | `<CreateYService>` | Deprecated. Avoid for new work. |
| <Name> | `<CreateZService>` | Recommended general-purpose choice. |

<!-- Notes carries the GUIDANCE a caller needs — which to pick, which to avoid and why — not a
     restatement of the algorithm's name. -->

<Paragraph on the optional parameters shared across these factory methods: what each controls, its
default (naming the shared defaults type where one exists), and the exception each throws on an
invalid value — e.g. "passing anything other than 224, 256, 384 or 512 throws `ArgumentException`".>

## Key types

| Type | Namespace | Role |
|------|-----------|------|
| `<ConcreteFactory>` | `<Namespace>` | Concrete factory. Implements `<IFactory>`. Create with `new`. |
| `<IFactory>` | `<Namespace>` | Factory interface. DI-friendly. |
| `<IService>` | `<Namespace>` | The service returned by the factory. |
| `<Defaults>` | `<Namespace>` | Shared defaults; `<Member>` is `<value>`. |

`<IService>` exposes <its primary method>:

```csharp
<ReturnType> <MethodName>(
    <Type> <param>,
    <Type>? <optionalParam> = null,
    CancellationToken cancellationToken = default);
```

<One short paragraph on what the result is and how to render/consume it, naming the helper or
extension that does so.>

<One short paragraph on how the type is obtained: the factory is constructed directly with `new`,
and the `I*` interfaces are DI-friendly, so `<ConcreteFactory>` can equally be registered against
`<IFactory>` in a Microsoft.Extensions.DependencyInjection container and injected where needed.>

## Usage

<!-- One ### sub-section per scenario, ordered simplest → most involved. Each snippet is complete
     and copy-pasteable, with its full using block. The final sub-section covers the cross-cutting
     concern (progress / cancellation / disposal) where the category has one. -->

### <Simplest scenario>

```csharp
using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using <Namespace>;

var factory = new <ConcreteFactory>();
<IService> service = factory.<CreateXService>();

// … the operation, end to end

Console.WriteLine(<result>);
```

### <Variation — a different algorithm, or a non-default parameter>

```csharp
using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using <Namespace>;

var factory = new <ConcreteFactory>();
<IService> service = factory.<CreateYService>(<namedParam>: <value>);

// … the operation

Console.WriteLine(<result>);
```

### <Cross-cutting concern — progress and cancellation>

<One or two sentences naming the optional parameters and when they earn their keep.>

```csharp
using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using <Namespace>;

var factory = new <ConcreteFactory>();
<IService> service = factory.<CreateXService>();

var progress = new Progress<int>(bytes => Console.WriteLine($"{bytes} bytes processed"));
using var cts = new CancellationTokenSource();

await using var input = File.OpenRead("large-input.bin");
var result = await service.<MethodAsync>(input, progress, cts.Token);
```

## Notes

<!-- Caveats that don't belong in a table. -->
- <Deprecated or broken options: provided for interoperability only; what to prefer instead.>
- <State requirements: e.g. the input stream is read to its end — position it at the start of the
  data before calling.>
- <Parameters that affect performance or memory but not the result.>
