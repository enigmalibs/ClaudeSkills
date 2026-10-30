# FEATURE-C001-PHASE02 — Windows update.ps1 and update.bat

## Summary

`scripts/windows/update.ps1` is the Windows twin of `scripts/linux/update.sh`: the same behaviour, output lines, summary and exit codes. Its target is `$env:CLAUDE_CONFIG_DIR`, else `%USERPROFILE%\.claude`.

It is written for Windows PowerShell 5.1: ASCII only, CRLF line endings, comment-based help (`Get-Help .\update.ps1`), and `-DryRun`. An unknown argument exits 2 with the usage.

Links:
- detected through `LinkType` (`SymbolicLink`, `Junction`);
- a link is removed with the item's own `.Delete()`, because 5.1's `Remove-Item -Recurse` follows directory links;
- the target listing is indexed by name, so a broken link still counts as present.

`scripts/windows/update.bat` (CRLF, no labels):
- runs `%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0update.ps1" %*`;
- passes the exit code back;
- pauses when its own name appears in `%CMDCMDLINE%` (a double-click), so the output stays readable.

README:
- the tree lists the Windows scripts;
- the copy-install paragraph names both platforms, the Windows target and `-DryRun`;
- the update line names `update.bat`.

## Files/modules touched

- Created: `scripts/windows/update.ps1`, `scripts/windows/update.bat`, `docs/done/FEATURE-C001-PHASE02.md`
- Modified: `README.md`, `docs/roadmap.md`, `docs/plan/FEATURE-C001.md`

## Deviations & follow-ups

- **Tested on PowerShell 7 on Linux, not on Windows.** Windows PowerShell 5.1 compatibility was checked statically (PSScriptAnalyzer's compatibility rules against the 5.1 profile; see the evidence). Before relying on Junction handling and the `.bat`, do one `update.bat -DryRun` and one real run on a Windows machine.
- **Double-click detection:** running `update.bat` from a PowerShell prompt also puts its name in `%CMDCMDLINE%`, so it pauses there too: one key press, no harm. Running it from `cmd` does not pause.
- **Links are resolved one hop** (the README's links point straight into the checkout). A chain of links into the checkout is treated as a foreign link: it is replaced by a copy, and its target is still never touched.
- **Name matching follows Windows:** case-insensitive (PowerShell hashtables). On a case-sensitive file system, two names that differ only in case would be treated as the same item.
- **Line endings:** besides PHASE01's `*.sh text eol=lf`, a `.gitattributes` could pin `*.bat text eol=crlf` and `*.ps1 text eol=crlf`. Recommendation only.
- The baseline of `html-report`'s suite is unchanged (1 failure + 1 error, already present before the run; see PHASE01).

## Decisions taken at build time

| Question                                       | Chosen                                                                                                                  | Why                                                                                                                               |
|------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| Unknown arguments                              | A plain script (no `[CmdletBinding()]`): extra arguments land in `$args` → usage, exit 2                                | An advanced script fails binding with PowerShell's own error and exit 1; this keeps the exit codes the same as `update.sh`        |
| How `powershell.exe` is found                  | Absolute `%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe`                                                  | Not affected by `PATH` order; it is present on every supported Windows                                                            |
| `find.exe` in the double-click check           | Absolute `%SystemRoot%\System32\find.exe`                                                                               | A Unix `find` earlier on `PATH` (Git, MSYS) would not understand `/i`                                                             |
| Removing the target item                       | Inlined in `Install-Item`; links through `.Delete()`, real items through `Remove-Item -Recurse -Force`                  | Clears PSScriptAnalyzer's `PSUseShouldProcessForStateChangingFunctions` warning on a one-use `Remove-*` helper (fix cycle 1 of 3) |
| Positional calls to the script's own functions | Kept                                                                                                                    | PSScriptAnalyzer `Information` only; named arguments would double the length of three internal calls                              |
| Errors                                         | One `try`/`catch`/`finally` around the run: `update.ps1: <message>` on stderr, exit 1; `finally` removes a staging copy | Probed that `finally` runs when `catch` calls `exit`                                                                              |

## Build/test evidence

Nothing to compile. Verification used PowerShell 7.6.9, installed as a .NET tool into the session scratchpad (`dotnet tool install PowerShell --tool-path …`). The repository and `~/.claude` were not touched.

- **Scenarios:** the PHASE01 harness, parameterized per platform, runs the same S1–S8 checks against `update.ps1` (`-DryRun`, `Get-Help` in place of `--help`). Result: **39 passed, 0 failed**. The same harness against `update.sh` also gives 39 passed, 0 failed.
- **Dangling links:** a broken link at `skills/avalonia` and at `commands/build.md`. Both scripts report `replace … (the link to … is replaced …)`, exit 0, and leave identical copies with no link behind.
- **PSScriptAnalyzer 1.25.0**, saved into the scratchpad:
  - `PSUseCompatibleSyntax` (targets 5.1 and 7.0), `PSUseCompatibleCommands` and `PSUseCompatibleTypes` (Windows PowerShell 5.1 profile `win-48_x64_10.0.17763.0_5.1.17763.316_x64_4.0.30319.42000_framework`): no finding. A probe with `??`, a ternary, `Get-Error` and `ConvertFrom-Json -AsHashtable` was flagged on all four lines, so the rules were active.
  - Default rules: 0 errors, 0 warnings, 3 `Information` (`PSAvoidUsingPositionalParameters`).
  - Parser: 0 parse errors.
- **Encoding:** `update.ps1` and `update.bat` are ASCII with CRLF line endings. `update.bat` has no `:label` and passes `%*` and `%ERRORLEVEL%` through. The `.bat` cannot run on Linux; it was verified by inspection.
- **Suites:**
  - `python3 -B -m unittest discover -s skills/dev-workflow/scripts`: 51 OK;
  - `… -s skills/html-report/scripts`: the baseline 1 failure + 1 error, unrelated.
- **Documentation sweep:** the README edits were this phase's planned steps. The *Install for one project* text (copies into `.claude/` of a project) is still accurate, because the scripts only target the user scope. There is no other prose doc.
