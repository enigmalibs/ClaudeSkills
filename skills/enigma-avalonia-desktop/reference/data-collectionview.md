# CollectionView (Data)

A WPF-style collection view layer in `Enigma.Avalonia.Desktop.Data`
(`xmlns:data="using:Enigma.Avalonia.Desktop.Data"`) for sorting, filtering and grouping over an
`IEnumerable` **without mutating the source**. Use `ObservableCollection<T>` (anything raising
`INotifyCollectionChanged`) so adds and removes reach the view on their own.

Two entry points: `CollectionViewSource` is the XAML/ViewModel-friendly wrapper — `Source` in, a live
`View` out, plus a `Filter` **event**. `CollectionView` is the projection itself, usable directly from
code.

## Key types

| Type | Role |
|---|---|
| `CollectionViewSource` | `AvaloniaObject` wrapper. `Source` : `IEnumerable?`, read-only `View` : `CollectionView?`, `SortDescriptions` / `GroupDescriptions` : `AvaloniaList<…>`, and a `Filter` event. Declarable in XAML. |
| `CollectionView` | The projection. `IList` + `INotifyCollectionChanged` + `INotifyPropertyChanged`. |
| `SortDescription` | Sort criterion: `PropertyName` : `string?`, `Direction` : `SortDirection`. Raises `DescriptionChanged`. |
| `PropertyGroupDescription` | Group criterion: `PropertyName` : `string?` + optional `ValueConverter` : `IValueConverter?`. Raises `DescriptionChanged`. |
| `CollectionViewGroup` | One group: `Key` : `object`, `Items` : `IReadOnlyList<object>`, `ItemCount` : `int`. What `Groups` is a list of. |
| `FilterEventArgs` | Carries `Item` into a `Filter` handler and `Accepted` (default `true`) back out. |
| `SortDirection` | Enum: `Ascending`, `Descending`. |

`CollectionView` members worth knowing: `SourceCollection`, `Filter` : `Predicate<object>?`,
`SortDescriptions`, `GroupDescriptions`, `Groups` : `IReadOnlyList<CollectionViewGroup>?`, `Count`,
`IsEmpty`, `this[int]`, `IndexOf`, `Contains`, `CopyTo`, `Refresh()`, `DeferRefresh()`. It is read-only:
every mutating `IList` member throws `NotSupportedException`.

## What refreshes, and what does not

`Refresh()` is the only thing that changes what the view contains. Filtering runs **first**, so sorting
and grouping only ever see the survivors; a `null` filter accepts everything.

| Change | `CollectionViewSource` | bare `CollectionView` |
|---|---|---|
| The source raises `CollectionChanged` | Refreshes | Refreshes |
| A description added to / removed from `SortDescriptions` or `GroupDescriptions` | Refreshes | **No refresh** |
| `SortDescription.PropertyName` / `.Direction` changed | Refreshes | **No refresh** |
| `PropertyGroupDescription.PropertyName` / `.ValueConverter` changed | Refreshes | **No refresh** |
| `Filter` assigned, or the state a filter reads changed | **No refresh** | **No refresh** |

Everywhere that table says "no refresh", the fix is a `Refresh()` call. Two sharp edges follow from it:

- **A freshly constructed `CollectionView` is empty until its first `Refresh()`** — the constructor
  subscribes but does not project.
- **A `CollectionViewSource.Filter` handler must be attached before `Source` is assigned** — the wrapper
  reads the event once, as `Source` is being assigned.

Only the **first** group description is applied; there is no nested grouping. `Groups` is `null` until a
group description is configured.

## Example — from code

```csharp
using System.Collections.ObjectModel;
using Enigma.Avalonia.Desktop.Data;

var people = new ObservableCollection<Person>(/* … */);
var view = new CollectionView(people);

view.SortDescriptions.Add(new SortDescription { PropertyName = "LastName", Direction = SortDirection.Ascending });
view.Refresh();                    // the constructor subscribes but does not project

using (view.DeferRefresh())        // one refresh at the end, not three
{
    view.Filter = item => ((Person)item).LastName.Length > 5;
    view.GroupDescriptions.Add(new PropertyGroupDescription { PropertyName = "Department" });
}

foreach (CollectionViewGroup group in view.Groups ?? [])
    Log($"{group.Key} ({group.ItemCount})");
```

## Example — `CollectionViewSource` in XAML

It is an ordinary resource: `Source` binds against the enclosing view's `DataContext`, the descriptions
are child elements, and `Filter` takes a code-behind handler. Bind list controls to `View`, or to
`View.Groups` for the grouped shape.

```xml
<UserControl xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:data="using:Enigma.Avalonia.Desktop.Data"
             xmlns:vm="using:MyApp.ViewModels"
             x:Class="MyApp.Views.PeopleView"
             x:DataType="vm:PeopleViewModel">

  <UserControl.Resources>
    <!-- Filter is declared before Source: the wrapper reads the event once, as Source is assigned. -->
    <data:CollectionViewSource x:Key="PeopleSource"
                               Filter="OnFilter"
                               Source="{Binding People}">
      <data:CollectionViewSource.SortDescriptions>
        <data:SortDescription PropertyName="LastName" Direction="Ascending" />
      </data:CollectionViewSource.SortDescriptions>
      <data:CollectionViewSource.GroupDescriptions>
        <data:PropertyGroupDescription PropertyName="Department" />
      </data:CollectionViewSource.GroupDescriptions>
    </data:CollectionViewSource>
  </UserControl.Resources>

  <StackPanel Spacing="12" Margin="16">
    <TextBlock Text="{Binding View.Count, Source={StaticResource PeopleSource}}" />

    <!-- Flat, sorted, filtered -->
    <ListBox ItemsSource="{Binding View, Source={StaticResource PeopleSource}}">
      <ListBox.ItemTemplate>
        <DataTemplate x:DataType="vm:Person">
          <TextBlock Text="{Binding LastName}" />
        </DataTemplate>
      </ListBox.ItemTemplate>
    </ListBox>

    <!-- Grouped: every item is a CollectionViewGroup -->
    <ItemsControl ItemsSource="{Binding View.Groups, Source={StaticResource PeopleSource}}">
      <ItemsControl.ItemTemplate>
        <DataTemplate x:DataType="data:CollectionViewGroup">
          <StackPanel Spacing="4" Margin="0,0,0,8">
            <TextBlock FontWeight="SemiBold"><Run Text="{Binding Key}" /><Run Text=" (" /><Run Text="{Binding ItemCount}" /><Run Text=")" /></TextBlock>
            <ItemsControl ItemsSource="{Binding Items}">
              <ItemsControl.ItemTemplate>
                <DataTemplate x:DataType="vm:Person">
                  <TextBlock Margin="12,0,0,0" Text="{Binding LastName}" />
                </DataTemplate>
              </ItemsControl.ItemTemplate>
            </ItemsControl>
          </StackPanel>
        </DataTemplate>
      </ItemsControl.ItemTemplate>
    </ItemsControl>
  </StackPanel>

</UserControl>
```

The handler receives one `FilterEventArgs` per item per refresh. `Accepted` starts at `true`, so
returning without touching it keeps the item.

```csharp
using Enigma.Avalonia.Desktop.Data;

private void OnFilter(object? sender, FilterEventArgs e)
    => e.Accepted = e.Item is Person person && person.Department == "Engineering";
```

## Example — driven from a ViewModel

Same wrapper, no code-behind — what you want when the filter reads ViewModel state. The view binds with
`ItemsSource="{Binding PeopleView.View}"` and `{Binding PeopleView.View.Groups}`.

```csharp
using System;
using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using Enigma.Avalonia.Desktop.Data;

public class PeopleViewModel : ObservableObject
{
    public ObservableCollection<Person> People { get; } = [ /* … */ ];
    public CollectionViewSource PeopleView { get; } = new();

    public PeopleViewModel()
    {
        // Before Source: the Filter event is read once, while Source is being assigned.
        PeopleView.Filter += OnFilter;
        PeopleView.SortDescriptions.Add(new SortDescription { PropertyName = "LastName" });
        PeopleView.Source = People;
    }

    public string FilterText
    {
        get;
        set { if (SetProperty(ref field, value)) PeopleView.View?.Refresh(); }  // filters never self-refresh
    } = "";

    private void OnFilter(object? sender, FilterEventArgs e)
        => e.Accepted = e.Item is Person p &&
                        (FilterText.Length == 0 || p.LastName.Contains(FilterText, StringComparison.OrdinalIgnoreCase));
}
```

## Common mistakes

- **A non-observable source** → a plain `List<T>` will not update the view on add or remove. Use
  `ObservableCollection<T>`.
- **Binding a list to the `CollectionViewSource` itself** → bind to its `View`, or `View.Groups`.
- **Forgetting the first `Refresh()`** on a hand-constructed `CollectionView` → it stays empty.
- **Changing the filter and expecting the view to follow** → nothing refreshes on a filter change. Call
  `Refresh()`.
- **Attaching `Filter` after assigning `Source`** → the handler is never read.
- **Expecting nested groups** → only the first group description is applied.
- **A `PropertyName` that does not match a real property** → empty or incorrect groups and ordering, not
  an exception.
- **Mutating the view** → every `IList` mutator throws `NotSupportedException`. Change the source
  collection instead.
