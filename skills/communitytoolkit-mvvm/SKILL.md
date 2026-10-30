---
name: communitytoolkit-mvvm
description: Use when writing or modifying ViewModels, observable properties, or commands with CommunityToolkit.Mvvm (MVVM Toolkit) — including whenever [ObservableProperty], [RelayCommand], or INotifyPropertyChanged boilerplate is about to be written.
metadata:
  version: "1.0.2"
---

# CommunityToolkit.Mvvm — explicit MVVM conventions

House rule: **no MVVM source generators.** Never use `[ObservableProperty]`, `[RelayCommand]`, `[NotifyPropertyChangedFor]`, `[NotifyCanExecuteChangedFor]`, or any other generator attribute — everything is declared explicitly. ViewModels derive from `ObservableObject` (CommunityToolkit.Mvvm package) and don't need to be `partial`.

## Observable properties

C# `field` keyword + `SetProperty`, single-line property:

```csharp
public string Test { get; set => SetProperty(ref field, value); } = string.Empty;
```

A non-nullable reference-type property gets an initializer (`= string.Empty;`, `= [];`, `= new();`) or an assignment in the constructor; where `null` is a legitimate value, declare it `T?` instead. Without one, `Nullable` + `TreatWarningsAsErrors` fail the build with CS9264. Value types need neither.

If side effects or dependent change notifications are needed, expand to a block body but keep the same `field`-based shape:

```csharp
public string FirstName
{
    get;
    set
    {
        if (SetProperty(ref field, value))
        {
            OnPropertyChanged(nameof(FullName));
        }
    }
} = string.Empty;
```

No manually declared backing fields — `field` is the backing store.

## Commands

Explicit, get-only properties typed as `RelayCommand`, `AsyncRelayCommand`, or their generic variants. Initialized in the constructor. Suffix every command property with `Command`. Handler methods (`OnSave`, `OnRefreshAsync`, …) are private.

```csharp
public RelayCommand SaveCommand { get; }
public AsyncRelayCommand RefreshCommand { get; }
public AsyncRelayCommand<Item> DeleteCommand { get; }

public MyViewModel()
{
    SaveCommand = new RelayCommand(OnSave, CanSave);
    RefreshCommand = new AsyncRelayCommand(OnRefreshAsync);
    DeleteCommand = new AsyncRelayCommand<Item>(OnDeleteAsync);
}
```

If `CanExecute` depends on observable state, call `NotifyCanExecuteChanged()` on the affected command from the relevant property setter.

## Common mistakes

| Mistake | Fix |
|---|---|
| `[ObservableProperty] private string _name;` | Explicit property: `public string Name { get; set => SetProperty(ref field, value); } = string.Empty;` |
| Non-nullable `string` property without an initializer | CS9264 under `Nullable` + `TreatWarningsAsErrors`: add `= string.Empty;` (or assign it in the constructor, or declare `string?`) |
| `[RelayCommand] private void Save()` | Get-only `SaveCommand` property + private `OnSave` handler |
| Manual backing field `private string _test;` | The `field` keyword is the backing store |
| Public command handler methods | Handlers stay private; only the `...Command` property is public |
| Command assigned in property initializer needing `this` | Initialize in the constructor |

Related: ViewModels are resolved via DI (see dotnet-di-design); async handlers follow dotnet-async.

If an existing codebase already uses the source-generator attributes, stay consistent with it and flag the divergence — never mix both styles in one project.
