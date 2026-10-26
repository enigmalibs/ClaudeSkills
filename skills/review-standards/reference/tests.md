# Tests — review-standards reference

Read this when reviewing `TEST`. The house skill still applies and is cited, not repeated: xunit-v3 (naming, project setup, the runner, parallelization, the v3/4.0 API notes and its *Common mistakes*). The baseline's `dotnet test` counts feed this dimension. The question is not "is coverage high" but "is the reviewed behaviour pinned by a test that would fail if it broke".

## Presence

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| No test project | no `*.UnitTests` / `*.IntegrationTests` project in the solution | High | create one per xunit-v3 (dotnet-solution-setup bootstrap step 10) |
| New behaviour without a test | the reviewed diff adds or changes a public method, a command handler or a branch, and no test in the diff or the suite references it | Medium; High for parsing, money, security, persistence | a test per behaviour, named after it |
| Bug fix without a regression test | a `fix(BUG-…)` diff with no new test that reproduces the bug | Medium | one that fails before the fix and passes after |
| Happy path only | no test with invalid input, an empty collection, a cancelled token, an I/O failure | Medium | one test per failure mode the code handles |
| Only integration tests for pure logic | a parser or calculator tested only through the whole app | Low | unit tests on the pure part |

## Assertions

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Assertion-free test | a `[Fact]` with no `Assert.`, or only `Assert.NotNull(result)` on a value that cannot be null | Medium | assert the outcome |
| Always-green test | `Assert.True(true)`, asserting on the input, `try { … } catch { }` around the act | High | a real assertion; `Assert.Throws<T>` for failures |
| Over-broad exception test | `Assert.ThrowsAny<Exception>`, `Assert.Throws<Exception>` | Low | the specific type |
| Vacuous collection assertion | `Assert.All` on a possibly empty collection without `throwIfEmpty: true` (xunit-v3 *New in 4.0*) | Low | `throwIfEmpty: true`, or assert the count first |
| Many behaviours in one test | 5+ asserts over unrelated outcomes; a test named `Test1` or `Works` | Low | one behaviour per test; `Method_Scenario_Expected` names |
| Snapshot of everything | a whole serialized object, HTML or XAML blob compared | Low | targeted assertions; a snapshot only for output formats |

## Isolation and determinism

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Timing-based | `Thread.Sleep`, `Task.Delay` to wait for something, `DateTime.Now` compared | Medium | an awaited signal, `TaskCompletionSource`, an injected `TimeProvider` |
| Shared mutable state | `static` fields set by tests; tests that pass only in name order; files at a fixed path | High | per-test fixtures, `IAsyncLifetime`, a temp directory per test |
| Real external resources | tests hitting the network, a real database, the user profile, the registry | Medium | fakes, or an `IntegrationTests` project with a skip condition (`Assert.SkipWhen`) |
| Cancellation ignored | async tests never passing `TestContext.Current.CancellationToken` (xunit-v3) | Low | pass it |
| `async void` test | fast-fails at runtime (xunit-v3) | Medium | `Task` |

## Coupling to implementation

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Testing private members | reflection into privates; `InternalsVisibleTo` used to test every internal | Low | test through the public behaviour |
| Mock-heavy verification | `Verify(x => x.Foo(), Times.Once)` as the only assertion; mocks of the type under test | Low | assert on outcomes; mock only I/O boundaries |
| Call order asserted | the sequence of collaborator calls checked when the behaviour does not require it | Low | assert the result |
| Expected value computed by the code under test | the same code path produces the expectation | Medium | literal expected values |

## Test code quality

- Tests follow the same `STYLE` rules as production code (usings per file, naming, no dead code) — report them under `TEST`, not `STYLE`.
- A test project that disables `TreatWarningsAsErrors` or `Nullable` is a `STYLE` finding (dotnet-solution-config).
- Tests marked `Skip` without a reason are one Medium finding listing them all.
