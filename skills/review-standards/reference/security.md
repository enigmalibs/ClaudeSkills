# Security — review-standards reference

Read this when reviewing `SEC`. No house skill covers these; `logging.md` of this skill covers what must never reach a log. Severity here follows exposure: input only the local user controls caps most findings at High; anything reachable from a file another person can author, a network or a URL handler is Critical.

## Secrets

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Secret in source | `password =`, `apiKey`, `token`, `connectionString` with a literal; base64 blobs; a `.pfx` in the tree | Critical | user secrets, environment or a vault; rotate the exposed value |
| Secret in a committed config | `appsettings*.json` with real credentials | Critical | placeholders in the repo; secrets from `IConfiguration` providers outside it |
| Secret in an exception message | `throw new Exception($"… {connectionString}")`; see `logging.md` *Sensitive data* for logs | Critical | never |
| Secret in the UI | a password in a plain `TextBox`; copied to the clipboard by default | High | a masked editor; clipboard only on an explicit action |

## Paths and files

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Path traversal | `Path.Combine(root, input)` without checking the result stays under `root` | Critical when the input is not the local user's, else High | `Path.GetFullPath` and a prefix check against `root` + separator; reject `..` |
| Insecure temp files | `Path.GetTempFileName()` then sensitive data; predictable names in `%TEMP%` | Medium | `Path.GetTempPath()` + `Path.GetRandomFileName()`, delete in `finally` |
| Overly permissive output | files created world-writable on Linux; shared folders | Low | an explicit `UnixFileMode`; user-profile paths |
| Archive extraction | `ZipFile.ExtractToDirectory` on an untrusted archive without per-entry path checks | High | validate every entry's full path |

## Injection

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| SQL from strings | `$"SELECT … WHERE Id = {id}"` handed to ADO, Dapper or `ExecuteSqlRaw` | Critical | parameters; EF Core's interpolated APIs (`FromSqlInterpolated`) |
| Command injection | `Process.Start("cmd", "/c " + input)`; `UseShellExecute = true` with user input | Critical | `ProcessStartInfo.ArgumentList`, `UseShellExecute = false` |
| URL or HTML from input | user text concatenated into a URL, or into HTML shown in a web view | High | `Uri.EscapeDataString`, `HtmlEncoder` |
| Regex from input | `new Regex(userInput)` without a timeout | Medium | `RegexOptions.NonBacktracking` or a `matchTimeout` |

## Deserialisation and parsing

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Unsafe deserialiser | `BinaryFormatter`, `SoapFormatter`, `NetDataContractSerializer`, `TypeNameHandling.All` | Critical | `System.Text.Json` with known types |
| XML external entities | `XmlDocument`/`XmlReader` with `DtdProcessing.Parse` or an `XmlResolver` on untrusted XML | High | `DtdProcessing.Prohibit`, `XmlResolver = null` |
| Unbounded input | a whole external file, stream or request read into memory with no size limit | Medium | a limit and a streaming parser |

## Transport and crypto

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| TLS validation disabled | `ServerCertificateCustomValidationCallback = (…) => true`, `DangerousAcceptAnyServerCertificateValidator` | Critical | validate; pin only with a documented reason |
| Weak algorithms | `MD5`, `SHA1`, `DES`, `RC2`, `TripleDES` for anything security-related; hand-rolled crypto | High | `SHA256`+, `AES-GCM`; `PBKDF2`/`Argon2` for passwords |
| Hard-coded IV or key | a constant `byte[]` IV or key | Critical | a random IV per message; the key from a store |
| `Random` for security | `new Random()` for tokens, salts, unguessable file names | High | `RandomNumberGenerator` |

## Data at rest and in the UI

| Check | How to spot it | Default | Fix |
|---|---|---|---|
| Sensitive data in plain settings | tokens or passwords in a user settings JSON | High | `ProtectedData` (Windows) or a credential store, or a stated reason the value is not sensitive |
| Clipboard and MRU leaks | sensitive values on the clipboard or in recent-files lists | Medium | explicit user action; exclude from MRU |
| Error details to the user | stack traces, paths, connection strings in dialogs | Low | a message; the detail goes to the log |
