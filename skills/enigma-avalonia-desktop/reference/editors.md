# Editors

Thirteen ready-to-use input controls in `Enigma.Avalonia.Desktop.Controls.Editors`
(`xmlns:editors="using:Enigma.Avalonia.Desktop.Controls.Editors"`). Every one derives from
`Avalonia.Controls.TextBox`, so caret handling, selection, clipboard, `MaxLength`, `PasswordChar`,
`PlaceholderText` and `IsReadOnly` behave exactly as on a stock text box. What the family adds is a title
above the input, a unit label and two content slots inside it, a validation message line below it, and —
on the typed editors — a strongly typed `Value` the control keeps in sync with `Text`.

Pick the editor whose CLR type matches the property you are binding. Bind `Value` (or `Text`, for the two
string editors) and set `Title`; parsing, formatting, error state and error display are the control's
job.

Parsing and formatting are **invariant-culture throughout**, and text that cannot be parsed is never
pushed to the binding: type `abc` into an `IntEditor` holding `42` and the editor sets its `:error`
pseudo-class, renders `Invalid value 'abc'` under the box, and leaves `Value` at `42`. The ViewModel
never sees the bad input, and correcting the text clears the error on the next keystroke.

## The editors

| Editor | Bound member | CLR type | Parsing |
|---|---|---|---|
| `TextEditor` | `Text` | `string?` | none — raw text |
| `MultiLineTextEditor` | `Text` | `string?` | none; ctor sets `AcceptsReturn = true`, `TextWrapping = Wrap`, `SelectAllTextOnFocus = false` |
| `ShortEditor` | `Value` | `short?` | `short.TryParse`, `NumberStyles.Integer` |
| `UShortEditor` | `Value` | `ushort?` | `ushort.TryParse`, `NumberStyles.Integer` |
| `IntEditor` | `Value` | `int?` | `int.TryParse`, `NumberStyles.Integer` |
| `UIntEditor` | `Value` | `uint?` | `uint.TryParse`, `NumberStyles.Integer` |
| `LongEditor` | `Value` | `long?` | `long.TryParse`, `NumberStyles.Integer` |
| `ULongEditor` | `Value` | `ulong?` | `ulong.TryParse`, `NumberStyles.Integer` |
| `SingleEditor` | `Value` | `float?` | `float.TryParse`, `NumberStyles.Float \| AllowLeadingSign` |
| `DoubleEditor` | `Value` | `double?` | `double.TryParse`, `NumberStyles.Float \| AllowLeadingSign` |
| `DecimalEditor` | `Value` | `decimal?` | `decimal.TryParse`, `NumberStyles.Number` |
| `HexadecimalEditor` | `Value` | `byte[]?` | `HexService.Decode` |
| `Base64Editor` | `Value` | `byte[]?` | `Base64Service.Decode` |

`DecimalEditor` is the one editor whose parse rule is looser than its siblings: `NumberStyles.Number`
accepts invariant group separators, so `1,999.99` is valid input. Every other numeric editor rejects a
comma outright rather than reinterpreting it, so a value can never change magnitude because of the
machine's locale.

**No editor declares a minimum, maximum or format property of its own.** Range checking belongs to the
bound property — the editor renders whatever `INotifyDataErrorInfo` reports. Cap input length with the
inherited `TextBox.MaxLength`.

## Base types

| Type | Role |
|---|---|
| `BaseEditor` | Base of every editor; extends `TextBox` with title, unit, leading/action slots, validation display and select-all-on-focus. Not abstract, but use `TextEditor` for plain text. |
| `BaseEditor<T>` | Abstract base for the typed struct editors (`where T : struct`). Adds `Value`, `FormatString`, `NullWhenEmpty` and the `TryParse` / `FormatValue` extension points. |
| `ByteArrayEditor` | Abstract `MultiLineTextEditor` that edits a `byte[]?` as encoded text. Base of the two binary editors. |

`Base64Editor` and `HexadecimalEditor` each hold a static `Enigma.Core.Encoding.Base64Service` /
`HexService` from the **Enigma.Core** package and call `Encode(byte[])` / `Decode(string)` on it.
Enigma.Core is a transitive dependency, so you never reference it yourself unless you use it directly.

## Properties

`BaseEditor` — all bindable styled properties:

| Property | Type | Default | Purpose |
|---|---|---|---|
| `Title` | `string?` | `null` | Label above the box. The row collapses entirely when null or empty. |
| `Unit` | `string?` | `null` | Trailing unit label (`kg`, `ms`, `px`) with a separator rule. Hidden when null or empty. |
| `PlaceholderText` | `string?` | `null` | Inherited from `TextBox`; the watermark while empty. |
| `LeadingContent` | `object?` | `null` | Arbitrary content in the leading slot, inside the border. |
| `ActionContent` | `object?` | `null` | Arbitrary content in the trailing action slot, inside the border. |
| `HasValidationError` | `bool` | `false` | Drives the `:error` pseudo-class. Settable, so a plain text editor can be error-flagged directly. |
| `ValidationErrorMessage` | `string?` | `null` | The message line's text. Visible only while `:error` is active. |
| `SelectAllTextOnFocus` | `bool` | `true` | Selects all text on focus. `MultiLineTextEditor` turns it off. |

`BaseEditor<T>` adds `Value` (`T?`, two-way by default, **data-validation enabled**), `FormatString`
(`string?` — a standard .NET numeric format such as `"N2"`, passed to
`ToString(string, IFormatProvider)` with `CultureInfo.InvariantCulture`) and `NullWhenEmpty` (`bool`,
default `false` — when true, empty text yields `null` instead of `default(T)`).

`ByteArrayEditor` adds only `Value` (`byte[]?`, two-way) — registered **without** data validation, unlike
`BaseEditor<T>.Value`.

## Example — XAML

```xml
<StackPanel xmlns:editors="using:Enigma.Avalonia.Desktop.Controls.Editors"
            xmlns:ei="https://github.com/josueclement/Enigma.Icons"
            Spacing="8">

  <editors:ShortEditor  Title="Temperature" Value="{Binding Temperature}" Unit="°C" />
  <editors:UShortEditor Title="Port"        Value="{Binding Port}" NullWhenEmpty="True" />
  <editors:DoubleEditor Title="Distance"    Value="{Binding Distance}" FormatString="N2" Unit="mm" />

  <editors:TextEditor Title="Search" Text="{Binding Query}">
    <editors:TextEditor.LeadingContent>
      <PathIcon Data="{ei:IconGeometry MagnifyingGlass}" Width="16" Height="16" />
    </editors:TextEditor.LeadingContent>
  </editors:TextEditor>

  <editors:TextEditor Title="Name" Text="{Binding Name}">
    <editors:TextEditor.ActionContent>
      <Button Content="Go" Padding="6,2" FontSize="12" />
    </editors:TextEditor.ActionContent>
  </editors:TextEditor>

  <editors:TextEditor Title="Password" PasswordChar="*" Text="{Binding Password}" />
  <editors:MultiLineTextEditor Title="Notes" Text="{Binding Notes}" Height="120" />

  <editors:HexadecimalEditor Title="Raw bytes" Value="{Binding Bytes}" />
  <editors:Base64Editor      Title="Encoded"   Value="{Binding Bytes}" />
</StackPanel>
```

## Example — validation from the ViewModel

`BaseEditor<T>.Value` is registered with data validation, so DataAnnotations on the bound property light
up the `:error` state automatically. Derive from `ObservableValidator` and pass `true` to `SetProperty`.

```csharp
using System.ComponentModel.DataAnnotations;
using CommunityToolkit.Mvvm.ComponentModel;

public class FormViewModel : ObservableValidator
{
    [Range(0, 10000)]
    public int? Quantity { get; set => SetProperty(ref field, value, true); } = 42;

    [Required, MaxLength(100)]
    public string? Name { get; set => SetProperty(ref field, value, true); } = "Hello";

    [Range(typeof(decimal), "0.01", "99999.99")]
    public decimal? Price { get; set => SetProperty(ref field, value, true); } = 99.95m;

    public byte[]? Bytes { get; set => SetProperty(ref field, value); } = [0x0A, 0xFF, 0x1B];
}
```

For a plain `TextEditor`, or for a rule DataAnnotations cannot express, set `HasValidationError` and
`ValidationErrorMessage` yourself.

## Styling

`:is(editors|BaseEditor)` is the selector that reaches all thirteen editors at once — every editor
derives from `BaseEditor`, so a style on the base type applies family-wide.

## Common mistakes

- **Binding a numeric editor's `Text` instead of `Value`** → bind `Value`; `Text` is the raw string the
  base `TextBox` manages.
- **Expecting culture-specific parsing** → invariant throughout. `FormatString` controls display only.
- **Expecting `Min`/`Max` on the control** → there is none. Validate the bound property.
- **Expecting validation styling without a validated property** → either use
  `SetProperty(ref field, value, true)` on an `ObservableValidator`, or set `HasValidationError`
  yourself. `ByteArrayEditor.Value` never data-validates.
- **Instantiating `ByteArrayEditor` or `BaseEditor<T>`** → both are abstract. Use `HexadecimalEditor` /
  `Base64Editor`, or the concrete typed editor.
