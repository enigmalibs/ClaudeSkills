---
name: git-repo-hygiene
description: Use when setting up or normalizing a .NET/Visual Studio git repository's text configuration — creating a .gitignore, .gitattributes, and .editorconfig, or fixing CRLF/LF line-ending churn (mixed endings, whole-file diffs) with git renormalize.
metadata:
  version: "2.0.1"
---

# git-repo-hygiene

Give a .NET repo consistent, cross-platform text: LF-normalized files, correct binary handling, a Visual Studio ignore set, and shared editor defaults.

## When to use

- Bootstrapping a new .NET / Visual Studio git repo that has no `.gitignore`, `.gitattributes`, or `.editorconfig`.
- Adding the missing one(s) to an existing .NET repo.
- Fixing line-ending churn — diffs dominated by CRLF↔LF changes, a "whole file changed" with no real edits, or mixed endings inside a file.

**Not for:** non-.NET repos (the bundled `.gitignore` is the Visual Studio template), or imposing code-style formatting rules (the `.editorconfig` here covers only line endings and charset). For a .NET **solution** that wants a full C# code-style file (naming, analyzer severities), use dotnet-solution-config's `.editorconfig` instead of the minimal one here — it is a strict superset of these line-ending/charset rules.

## The three files

| File | Purpose | Source |
|------|---------|--------|
| `.gitignore` | Ignore VS/dotnet build output, caches, and tool artifacts (plus Rider `.idea/`). | Frozen copy of GitHub's `VisualStudio.gitignore` — `templates/gitignore`. |
| `.gitattributes` | Normalize all text to **LF** in the repo, keep `.bat`/`.cmd` as CRLF, force known binaries (`*.bin` included — test fixtures and blobs must never be converted). | `templates/gitattributes`. |
| `.editorconfig` | Editor defaults: LF, final newline, UTF-8 (CRLF for `.bat`/`.cmd`). | `templates/editorconfig`. |

## Workflow — create only if missing

For each of the three files, in the target repo root:

1. If the file **does not exist**, copy the matching template to its dotted name: `templates/gitignore` → `.gitignore`, `templates/gitattributes` → `.gitattributes`, `templates/editorconfig` → `.editorconfig`.
2. If the file **already exists**, do **not** overwrite it. Report that it exists and show a diff against the template so the user decides what (if anything) to merge.

Never clobber a repo's existing config — an established `.gitignore` often carries project-specific entries.

## Normalizing line endings

Once `.gitattributes` is in place (newly added or already present), line endings are re-applied by **the user**, not by this skill. Present these commands for them to run:

```
git add --renormalize .
git status
git commit -m "Normalize all line endings to LF"
```

This skill does **not** run these or commit them — the user owns when and whether to normalize (see the `dev-workflow` skill).

## Bundled files

- [`templates/gitignore`](templates/gitignore) — Visual Studio / dotnet ignore set (+ Rider `.idea/`).
- [`templates/gitattributes`](templates/gitattributes) — LF normalization + binary rules.
- [`templates/editorconfig`](templates/editorconfig) — editor line-ending/charset defaults.

Branching, commits, and line-ending ownership are governed by the `dev-workflow` skill — this skill does not restate them.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Overwriting an existing `.gitignore`/`.gitattributes` | Create only if missing; diff, don't clobber. |
| Running `git add --renormalize` or committing it yourself | Present the commands; the user runs and commits them. |
| Naming a bundled template `.gitignore` (with a dot) | Keep bundled names un-dotted (`templates/gitignore`) so they don't act as real ignore files inside this skill folder. |
| Expecting it to fire for a non-.NET repo | The `.gitignore` is VS-specific; scope is .NET / Visual Studio. |
