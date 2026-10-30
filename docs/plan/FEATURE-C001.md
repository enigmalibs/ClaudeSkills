**Status:** TODO
**Type:** FEATURE (multi-phase)
**Branches:** feature/feature-c001-phase01-linux-update · feature/feature-c001-phase02-windows-update
**Run:** feature/2026-10-30-update-scripts

# FEATURE-C001 — Skill and command update scripts

## Objective

A `scripts/` folder at the repository root with one update script per platform — `scripts/linux/update.sh`, and `scripts/windows/update.ps1` plus the `update.bat` launcher — that copies this checkout's skills and commands into the user's Claude folder, replacing same-named items and never removing anything else, with a dry run that works whatever the target holds.

## Context & constraints

- Sources: every folder under `skills/` (17 today) and every `commands/*.md` (5 today). The repository root is two levels above each script (`scripts/<platform>/`).
- Target: `$CLAUDE_CONFIG_DIR` when set, else `~/.claude` (Linux) / `%USERPROFILE%\.claude` (Windows) — Claude Code's user-scope folder; skills in `<target>/skills/<name>/`, commands in `<target>/commands/<name>.md`.
- The README installs by symbolic links (one per skill folder / command file) or by plain copies "re-copied to update". A target may therefore hold copies, links into this checkout, links elsewhere, and items that are not in this repository (another skill, a namespaced command subfolder) — this machine's has `draw-diagram` and `synced`, and a stale `review-standards/templates/report.html` this repository has deleted.
- Windows PowerShell 5.1 is the only PowerShell guaranteed on Windows: no PowerShell 7-only syntax, and it reads BOM-less scripts as ANSI, so the `.ps1` stays ASCII. It refuses to run downloaded `.ps1` files under the default execution policy — hence the `.bat`.
- Line endings are mixed in the repository (Windows-authored files CRLF, Linux-authored LF) and there is no `.gitattributes`; line endings are never normalized by a dev.
- No `pwsh` or `shellcheck` on the build machine; the .NET SDK is.

## Decisions

See *Decisions taken autonomously*. Shared behaviour of both scripts:

- **Per item**, in this order of checks:
  - `linked` — the target item is a link resolving to the source item: left as is.
  - `replace` — the target item exists (folder, file or a link elsewhere): the source is copied to a staging path beside it (`.<name>.update-<pid>`), the old item is removed — a link by removing the link only, never what it points to — and the staging path is renamed into place.
  - `add` — the target item does not exist: copied the same way.
- **Everything else** in `<target>/skills` and `<target>/commands` is listed as `keep` and never touched.
- **Missing target folders** (`<target>`, `skills`, `commands`) are created — printed as `create`.
- **Guard**: when a target folder resolves to this checkout's own `skills/` or `commands/`, that folder is skipped with a message (every item would already be the source).
- **Dry run** (`--dry-run` / `-n`; `-DryRun`): the same lines under a `Dry run - nothing is changed.` header, no write of any kind; it never fails because a target folder is missing or empty.
- **Output**: a header naming the source checkout and the target, one section per folder, one line per item (`create`, `add`, `replace`, `linked`, `keep`), then one summary line with the counts. ASCII only.
- **Exit codes**: `0` done (dry run included) · `1` error (no `skills/` + `commands/` beside `scripts/`, a target path that is a file, a failed copy) · `2` usage (unknown argument).

## PHASE01 — Linux update.sh

**Status:** TODO

### Steps

1. `scripts/linux/update.sh` (bash, `#!/usr/bin/env bash`, `set -euo pipefail`, LF endings, mode `100755`):
   - `--dry-run` / `-n`, `--help` / `-h`; anything else prints the usage to stderr and exits 2.
   - Resolves the repository root from `${BASH_SOURCE[0]}`; exits 1 when `skills/` or `commands/` is missing there.
   - Target per *Context*; the shared behaviour per *Decisions*, links detected with `[ -L ]` and resolved with `readlink -f`; staging cleaned up by an `EXIT` trap.
2. README:
   - the repository tree gains `scripts/` (`linux/update.sh`);
   - *Install for every project* gains the copy-based alternative through the script (the `cp` sentence is replaced);
   - *Update and uninstall* names the script for copy installs.

### Acceptance criteria

Run against throwaway targets (`CLAUDE_CONFIG_DIR` in the scratchpad), never the real `~/.claude`:

- Dry run with the target missing, with empty `skills/` and `commands/`, and with a populated target: exit 0, `create` / `add` / `replace` / `keep` lines as expected, and the target byte-for-byte unchanged (or still absent).
- Real run on a populated target holding foreign skills and commands (a folder, a namespaced command subfolder, a plain file): every repo item matches its source (`diff -r`), a stale file inside a repo skill is gone, every foreign item is untouched, no staging path is left.
- A target item that is a link into this checkout is reported `linked` and left; a link elsewhere is replaced by a copy while its target folder is untouched.
- A target `skills` folder that is a link to this checkout's `skills/` is skipped and the checkout is unchanged.
- An unknown argument exits 2 with the usage; a script copy outside a checkout exits 1.
- `bash -n` passes; the file is LF, executable in the index; both Python suites still pass.

## PHASE02 — Windows update.ps1 and update.bat

**Status:** TODO

### Steps

1. `scripts/windows/update.ps1` (CRLF, ASCII, Windows PowerShell 5.1-compatible): comment-based help; `[CmdletBinding()] param([switch] $DryRun)`; `Set-StrictMode -Version Latest`, `$ErrorActionPreference = 'Stop'`; repository root from `$PSScriptRoot`; target per *Context*; the shared behaviour per *Decisions*. A link is detected through its `LinkType` (`SymbolicLink`, `Junction`) and removed with the item's own `.Delete()` — never `Remove-Item -Recurse`, which follows directory links in 5.1; a real folder is removed with `Remove-Item -Recurse -Force`. Staging cleaned up in a `finally`.
2. `scripts/windows/update.bat` (CRLF): runs `powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0update.ps1" %*`, passes its exit code back, and pauses when started by a double-click (the script's name in `%CMDCMDLINE%`); no labels or `goto`.
3. README: the tree gains `windows/update.ps1` + `update.bat`; the install and update text names the Windows script next to the Linux one.

### Acceptance criteria

- With PowerShell available on the build machine (a tool install in the scratchpad), the PHASE01 scenarios — dry run on a missing, empty and populated target, real run with foreign items, the two link cases, the guard — pass with the same results as `update.sh`; otherwise each is verified by inspection and the done doc says so.
- The script parses without errors; it has no non-ASCII byte and no PowerShell 7-only syntax (`??`, `?.`, ternary, `-Parallel`, `&&`/`||` pipeline chains).
- `update.bat` passes `%*` and the exit code through and contains no label; both files are CRLF.
- README tree and text name all three scripts; links resolve and tables stay aligned; both Python suites still pass.

## Out of scope

- Updating the checkout itself (`git pull`) — the scripts install what the checkout holds.
- Removing installed items this repository no longer ships (they cannot be told apart from the user's own).
- Project-scope installs (`<project>/.claude/`), a macOS-specific script, an uninstall script.
- Adding a `.gitattributes` or normalizing line endings.
- A committed test suite for the scripts.

## Decisions taken autonomously

| Question                        | Chosen                                                                                                                                                                  | Why                                                                                                                                                     | Alternatives rejected                                                                                       |
|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| What "replace" means            | Each repo skill folder / command file replaces the same-named target item whole; every other item is listed `keep` and never touched                                    | The draft forbids removing other skills or commands; a whole-folder swap also drops files a repo skill no longer ships (`report.html` on this machine)  | Overlay copy (`cp -r skills/*`) — leaves stale files inside a skill; mirroring the folders — deletes others |
| Dry-run interface               | `--dry-run` / `-n` on Linux, `-DryRun` on Windows (passed through by the `.bat`)                                                                                        | Explicit and symmetric; `update.bat -DryRun` works from cmd and Explorer shortcuts                                                                      | `-WhatIf` via `SupportsShouldProcess` (no Linux twin, noisier output)                                       |
| Missing or empty target folders | Dry run reports `create` and `add` and exits 0; a real run creates them                                                                                                 | The draft's dry-run requirement; a first install is the same operation as an update                                                                     | Refuse when the folders are missing (forces a manual `mkdir`)                                               |
| Target folder                   | `$CLAUDE_CONFIG_DIR` when set, else `~/.claude` / `%USERPROFILE%\.claude`                                                                                               | Claude Code reads its user scope from there; it also lets every test run against a throwaway folder                                                     | Hard-coded `~/.claude` only; a `--target` argument (a second way to say the same thing)                     |
| An existing link at the target  | Link into this checkout → `linked`, left as is; link elsewhere → the link alone is removed, then copied over; a target folder that *is* the checkout's folder → skipped | Keeps a linked install live and never deletes through a link — the one way these scripts could destroy files they do not own                            | Always replace links (silently turns a linked install into copies); follow links (deletes the clone)        |
| Partial failure                 | Copy to a sibling staging path, then remove and rename; the staging path is cleaned up on exit                                                                          | A failed copy leaves the previous version in place instead of a half-written skill                                                                      | Remove then copy (a failed copy leaves the skill missing)                                                   |
| What the `.bat` does            | `powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File` with `%*` and the exit code passed through; pauses when double-clicked                                | Bypass applies to that process only; a `.ps1` cannot be double-clicked, so the `.bat` is the double-click entry point and its output must stay readable | `pwsh` (not installed by default); always pause (breaks scripted use); never pause (output vanishes)        |
| PowerShell compatibility        | Windows PowerShell 5.1-safe and ASCII-only (also runs on 7)                                                                                                             | 5.1 is on every Windows; it reads BOM-less files as ANSI, so non-ASCII text would be mangled                                                            | PowerShell 7-only script; a UTF-8 BOM (invisible in diffs, easy to lose)                                    |
| Line endings of the new files   | `.sh` LF; `.ps1` and `.bat` CRLF; a `.gitattributes` rule is only recommended                                                                                           | Bash fails on CRLF and cmd is safest with CRLF; normalization stays the user's call                                                                     | Adding `.gitattributes` in this item                                                                        |
| Tests                           | Scenario runs against throwaway targets, recorded in the completion docs; no committed suite                                                                            | The draft names exactly three files; the scenarios give the same evidence for scripts that rarely change                                                | A `test_update.py` per platform (new test infrastructure for shell scripts)                                 |
| Pulling the checkout first      | No — the scripts install the checkout as it is                                                                                                                          | Pulling mixes source control into an installer and fails on a dirty or detached clone                                                                   | `git pull` before copying                                                                                   |
| Phasing                         | PHASE01 Linux script + README; PHASE02 Windows scripts + README                                                                                                         | One platform per review (~30 min each); each commit leaves the README describing exactly what exists                                                    | One phase; a README-only third phase (too small to review alone)                                            |
