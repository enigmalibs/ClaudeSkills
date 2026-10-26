# MSI profiles — dotnet-release reference

Read this before **offering an MSI profile** for an app. The core `SKILL.md` still applies: the execution boundary, the version bump and release notes, and the runbook.

## MSI profiles (apps only)

When releasing an **app** — never a library — **offer** to generate a home-made MSI profile: a JSON file WixSharp turns into a Windows installer. The offer fires in the app branch only, **after** the version bump / release notes and **before** the printed runbook. It is **opt-in** — the skill suggests, the user says yes/no. A project with a `PackageId` (a packable library) never gets a profile.

**GUID contract** — the whole point of persisting these files:

- `upgradeCode` — the app's **stable identity** GUID; the **same in every version's profile**.
- `productId` — a **new GUID for every version**.

**Location & filenames.** Profiles live in `<solution-root>/msiProfiles/` (create the dir if missing) and are **committed** to the repo — the `upgradeCode` must persist across releases. Filenames are **always version-suffixed**, including the first: `<AppName>.msiprofile.<version>.json`. Detect this app's existing profiles by glob `<AppName>.msiprofile.*.json`; an empty or absent dir counts as "first".

**First profile** (none exist for this app): generate **two** GUIDs — `upgradeCode` and `productId` — then fill the rest by auto-detecting the derivable fields and confirming/asking the others.

- **Auto-detect:** `appName` + `msiFilename` (csproj / app name); `releasePath` = `<appdir>\bin\Release\<tfm>`; the shortcut exe / `targetPath` = the app's **build-output assembly name**, `[INSTALLDIR]\<AssemblyName>.exe` (the csproj output name — often differs from the display `appName`, e.g. `Draw.App.exe` for the `Draw` app); `productIcon` = `Assets\*.ico`; `manufacturer` = csproj `<Authors>` / `<Company>`; `version` = the release `X.Y.Z`. If the `.ico` or a `bin\Release\<tfm>` build isn't present yet, leave that field blank and **warn**.
- **Confirm/ask, with defaults:** `scope` (`PerMachine`), `installPath` (`%ProgramFiles%\<AppName>`), `compression` (`High`), `outputPath`, and `shortcuts` (default a `%Desktop%` and a `%ProgramMenu%` entry, both targeting `[INSTALLDIR]\<AssemblyName>.exe`).

**Subsequent profile** (≥1 already exists): **clone the most-recent** `<AppName>.msiprofile.*.json` (highest version). Keep `upgradeCode` and all config **verbatim**; generate a **new `productId`** only; set `version` = the release version. Re-point `releasePath` **only if** this release changed the app's TFM (see `SKILL.md` *In-repo edits*). If the newest existing profile is malformed, **stop and ask** — don't guess.

**GUID generation — the skill runs it.** Use a local generator: `uuidgen`, or `cat /proc/sys/kernel/random/uuid`, or PowerShell `[guid]::NewGuid()`. It is the first of the two run-permitted exceptions in `SKILL.md`'s *Execution boundary*. **Never fabricate a GUID** by hand.

**Scope stops at the JSON profile** — no `.msi` build, no WixSharp invocation.

### Field reference

Mirrors [`templates/msiprofile.template.json`](../templates/msiprofile.template.json) (its field **order** is authoritative).

| Field | Meaning | Source |
|---|---|---|
| `appName` | Display name (drives `installPath`, shortcut names, `msiFilename`) | csproj / app name — confirm |
| `installPath` | Install directory | default `%ProgramFiles%\<AppName>` — confirm |
| `releasePath` | Build output to package | `<appdir>\bin\Release\<tfm>` — auto (blank + warn if not built) |
| `scope` | Install scope | default `PerMachine` — confirm |
| `version` | Release version | the release `X.Y.Z` — auto |
| `productId` | Per-version product GUID | **generated new every release** |
| `upgradeCode` | Stable app-identity GUID | **generated once; reused verbatim after** |
| `manufacturer` | Publisher | csproj `<Authors>` / `<Company>` — auto |
| `productIcon` | App icon (`.ico`) | `Assets\*.ico` — auto (blank + warn if absent) |
| `compression` | MSI compression | default `High` — confirm |
| `outputPath` | Where the `.msi` is written | confirm |
| `msiFilename` | `.msi` base name | csproj / app name — confirm |
| `shortcuts[]` | Desktop / start-menu shortcuts | default `%Desktop%` + `%ProgramMenu%`, target `[INSTALLDIR]\<AssemblyName>.exe` |

Each `shortcuts[]` entry, in order: `shortcutPath` (`%Desktop%` / `%ProgramMenu%`), `shortcutName`, `targetPath` (`[INSTALLDIR]\<AssemblyName>.exe`), `iconPath`, `arguments`.

**Placeholder legend** (tokens in the template): `{{APP_NAME}}`, `{{INSTALL_PATH}}`, `{{RELEASE_PATH}}`, `{{SCOPE}}`, `{{VERSION}}`, `{{PRODUCT_ID}}`, `{{UPGRADE_CODE}}`, `{{MANUFACTURER}}`, `{{PRODUCT_ICON}}`, `{{COMPRESSION}}`, `{{OUTPUT_PATH}}`, `{{MSI_FILENAME}}`, and `{{TARGET_EXE}}` (the shortcut target exe filename, e.g. `Draw.App.exe`). Write valid JSON; a non-ASCII `manufacturer` need not be `\uXXXX`-escaped (the examples' escaping is cosmetic).

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Generating an MSI profile for a *library* | Profiles are apps-only; a project with a `PackageId` never gets one. |
| Regenerating `upgradeCode` on a later release | Reuse the existing `upgradeCode` verbatim — only `productId` changes per version. |
| Fabricating GUIDs by hand | Run a local generator (`uuidgen` / `[guid]::NewGuid()`); GUIDs are never invented. |
| Storing MSI profiles outside `<solution-root>/msiProfiles/` | They live there and are committed, so `upgradeCode` persists across releases. |
