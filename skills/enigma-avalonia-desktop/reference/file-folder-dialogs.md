# File & Folder pickers

`IFileDialogService` and `IFolderDialogService` (`Enigma.Avalonia.Desktop.Services`) put Avalonia's
`IStorageProvider` behind an injectable interface, so a ViewModel can raise a picker without seeing a
`Window`.

They need the provider set once at startup —
`service.SetStorageProvider(mainWindow.StorageProvider)` in
`App.OnFrameworkInitializationCompleted` (see `setup.md`). Using one before that throws
`InvalidOperationException("Storage provider is not set")`.

## Two API layers

**The interfaces** — Avalonia storage items in, options objects out:

- `IFileDialogService`
  - `IStorageProvider? StorageProvider { get; }`
  - `void SetStorageProvider(IStorageProvider storageProvider)`
  - `Task<IReadOnlyList<IStorageFile>> ShowOpenFileDialogAsync(FilePickerOpenOptions options)`
  - `Task<IStorageFile?> ShowSaveFileDialogAsync(FilePickerSaveOptions options)`
- `IFolderDialogService`
  - `IStorageProvider? StorageProvider { get; }`
  - `void SetStorageProvider(IStorageProvider storageProvider)`
  - `Task<IReadOnlyList<IStorageFolder>> ShowOpenFolderDialogAsync(FolderPickerOpenOptions options)`

**The string-path extension overloads** — simpler, and what you usually want. They live in
`FileDialogServiceExtensions` / `FolderDialogServiceExtensions` and **require
`using Enigma.Avalonia.Desktop.Services;`** to be visible:

```csharp
using System.Collections.Generic;
using System.Threading.Tasks;
using Avalonia.Platform.Storage;

Task<IEnumerable<string>> ShowOpenFileDialogAsync(
    string? title = null,
    bool allowMultiple = false,
    string? suggestedStartLocation = null,
    string? suggestedFileName = null,
    IReadOnlyList<FilePickerFileType>? fileTypeFilter = null);

Task<string?> ShowSaveFileDialogAsync(
    string? title = null,
    string? suggestedStartLocation = null,
    string? suggestedFileName = null,
    string? defaultExtension = null,
    bool showOverwritePrompt = true,
    IReadOnlyList<FilePickerFileType>? fileTypeChoices = null);

Task<IEnumerable<string>> ShowOpenFolderDialogAsync(
    string? title = null,
    bool allowMultiple = false,
    string? suggestedStartLocation = null,
    string? suggestedFileName = null);
```

Prefer these unless you need `IStorageFile` handles for streaming.

## Example

```csharp
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Avalonia.Platform.Storage;
using CommunityToolkit.Mvvm.ComponentModel;
using Enigma.Avalonia.Desktop.Services;

public class DocumentsPageViewModel(
    IFileDialogService fileDialogs,
    IFolderDialogService folderDialogs) : ObservableObject
{
    private readonly IFileDialogService _files = fileDialogs;
    private readonly IFolderDialogService _folders = folderDialogs;

    private async Task OpenOneAsync()
    {
        var files = await _files.ShowOpenFileDialogAsync(title: "Select a file", allowMultiple: false);
        var path = files.FirstOrDefault();          // null if cancelled
    }

    private async Task OpenTextFilesAsync()
    {
        var txt = new FilePickerFileType("Text files")
        {
            Patterns = ["*.txt", "*.md"],
            MimeTypes = ["text/plain", "text/markdown"],
        };

        var files = await _files.ShowOpenFileDialogAsync(
            title: "Select text files",
            allowMultiple: true,
            fileTypeFilter: [txt, FilePickerFileTypes.All]);
    }

    private async Task SaveAsync()
    {
        var path = await _files.ShowSaveFileDialogAsync(
            title: "Save document",
            suggestedFileName: "document",
            defaultExtension: "txt",
            fileTypeChoices: [new FilePickerFileType("Text file") { Patterns = ["*.txt"] }]);
        // path is null if cancelled
    }

    private async Task PickFolderAsync()
    {
        var folders = await _folders.ShowOpenFolderDialogAsync(title: "Select a folder");
        var dir = folders.FirstOrDefault();
    }

    private async Task StreamAsync()   // when you need the handle, not the path
    {
        var picked = await _files.ShowOpenFileDialogAsync(new FilePickerOpenOptions
        {
            Title = "Import",
            AllowMultiple = false,
        });

        if (picked.Count == 0) return;
        await using var stream = await picked[0].OpenReadAsync();
        // …
    }
}
```

## Notes

- **The extension overloads project the selection with `IStorageItem.TryGetLocalPath()` and drop every
  item that has none**, so the returned sequence can be **shorter** than what the user picked. When that
  matters, use the options overloads and keep the handles.
- **`suggestedStartLocation` is resolved with `TryGetFolderFromPathAsync`**; a path that does not exist
  resolves to `null` and the dialog opens at the platform default. It is never an error.
- **`SetStorageProvider` validates nothing and can be called again** — the last provider wins, which is
  what a replacement main window needs. `StorageProvider` is readable on both interfaces, so a caller can
  check readiness (`is not null`) and probe `CanOpen`, `CanSave` or `CanPickFolder` before offering the
  action.
- **Dialogs are modal to the window that owns the provider.** Call them from the UI thread; awaiting the
  task keeps the caller on it.

## Common mistakes

- **Missing `using Enigma.Avalonia.Desktop.Services;`** → the string-path overloads (`title:`,
  `allowMultiple:`, …) are invisible and the compiler only sees the options-object methods, so the call
  fails to resolve.
- **Calling a picker before `SetStorageProvider`** → `InvalidOperationException("Storage provider is not
  set")`.
- **Expecting an exception on cancel** → open dialogs return an **empty sequence**, save returns `null`.
- **Assuming the returned count matches the selection** → see the `TryGetLocalPath()` note above.
