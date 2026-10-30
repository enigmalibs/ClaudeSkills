---
name: dotnet-release
description: Use when releasing a new version of a .NET library/app to NuGet — bumping the version, authoring the release documentation from the bundled templates (packed README + badges, release notes, per-category guides and their index, SECURITY.md), PackageReleaseNotes, refreshing NuGet packages, printing the pack/tag/push runbook, and generating a WixSharp MSI profile when releasing an app.
metadata:
  version: "7.2.0"
---

# .NET version release

Drive a new NuGet library-version release end-to-end: make the in-repo edits (version, release notes, README, package metadata, selective dependency bumps), then **print** the out-of-repo runbook for the user to run. A release is a **`FEATURE-HHHH` work item** — one phase for a routine bump, four for a first release (see *The shape of a release work item*). **dev-workflow** owns its mechanics (see *Cross-references*); this skill does not restate them.

This file carries the routine release. **Read [`reference/first-release.md`](reference/first-release.md) before a first release** — or when pack-verify finds package metadata missing or a `.snupkg` — and **[`reference/msi-profiles.md`](reference/msi-profiles.md) before offering an MSI profile** for an app.

## When to use

- Cutting a new version of a .NET **library** that publishes to NuGet — bump the version, refresh notes and README, update dependencies, and produce the pack/tag/push runbook.
- Cutting a new version of a non-packable **app** — the version bump, release notes, and tag still apply; the `pack`/`push` steps are skipped (see *App vs library*).

**Not for:** the shape of `Directory.Packages.props` / CPM itself (see **dotnet-solution-config**) · `.gitignore` / `.gitattributes` / line-ending normalization (see **git-repo-hygiene**) · the roadmap / plan / `done` / commit / branch mechanics of the work item (see **dev-workflow**).

## Execution boundary

The skill makes **in-repo edits only**, and the boundary has **exactly two** run-permitted exceptions — both local and reversible, unlike the outward-facing commands:

- **Runs:** local **GUID generation** for an app's MSI profile (`reference/msi-profiles.md`); and the local **pack-verify** below, which cleans up after itself.
- **Prints only, never runs:** `git tag`, `git push`, the publish `dotnet pack` into a real artifacts directory, `dotnet nuget push`, and the merge/push to the default branch. The NuGet API key is never stored, committed, or echoed.

This mirrors **git-repo-hygiene** and **dev-workflow**: the user owns commits, tags, and publishes.

### Pack-verify (local, then deleted)

Before printing the runbook, pack once into a throwaway directory and **inspect the artifact** — the only way to catch bad metadata before it is published irreversibly:

```bash
dotnet pack <lib.csproj> -c Release -o ./artifacts/verify   # then inspect, then delete
```

Confirm, from the `.nupkg` and the nuspec it contains:

- the **`.nupkg` version** matches the release `X.Y.Z`;
- the verify directory holds **the `.nupkg` and nothing else** — no `.snupkg` (the symbols rule, in `reference/first-release.md`);
- **`README.md` is embedded and non-empty** (an empty packed README is a silent nuget.org landing-page failure);
- **`LICENSE.md` is embedded**;
- the nuspec's **`<version>`, `<title>`, `<license type="file">`, `<readme>` and `<releaseNotes>`** are all correct;
- the **dependency floors** are what you expect, per target framework.

Then **delete the verify directory** — it is a scratch artifact and is never committed; it sits under `artifacts/`, which the house `.gitignore` (**git-repo-hygiene**) already ignores. The publish `pack` (into `./artifacts`) stays print-only in the runbook.

## In-repo edits (the skill makes these)

Given the version `X.Y.Z` being released, take **one** of two paths — which one depends on whether a version of this package is already published on nuget.org:

- **First release** (no published version yet) — package metadata, the third-party license audit, the release documents and `docs/RELEASE.md`: follow [`reference/first-release.md`](reference/first-release.md).
- **Routine release** (a published version exists) — below.

### Routine release

1. **`<Version>`** in the packable library `.csproj` → `X.Y.Z`. (A CLI/app in the same solution keeps its own independent `<Version>`.) Normalize the **target frameworks** if the set moves — propose → confirm → log; see *Target-framework normalization*.
2. **`<PackageReleaseNotes>`** in that csproj — a short prose summary mirroring the top of `RELEASENOTES.md`, ending with `See RELEASENOTES.md for the full details.` (or the migration guide, for a breaking release). **Prepend** the new `RELEASENOTES.md` section, update the README **what's-new callout**, and the **supported target frameworks** line *only* if the TFM set moved. See *Release documents*.
3. **Dependency refresh** — see *NuGet package refresh*.
4. **Re-run the snippet-verification gate** — only if the guides or the README quick-start were touched this release. See *Release documents → Guides*.

So the actual per-release version edits are usually just `<Version>` in the csproj and the what's-new callout — plus the target-framework normalization on the releases that move the TFM set. The NuGet badge tracks the published version on its own — leave it alone.

### Target-framework normalization

Check the **packable library**'s `<TargetFramework>` / `<TargetFrameworks>` and normalize its modern-.NET set to the **house set** — defined, dated and reviewed once in **dotnet-solution-setup** (*Target frameworks*); this skill carries no TFM list of its own. **This is the one in-repo edit the skill proposes and confirms before writing:** show the `old → new` TFM set and wait for the user's OK, because a TFM change moves the library's compatibility surface. Apps/CLIs are left alone (they ship a single TFM).

- **Preserve** every `netstandard*` target (max consumer compatibility) and every **platform-specific** TFM (one with a `-` suffix — `net8.0-windows`, `net10.0-android`, …); rewriting those would strip the platform surface. If a platform-specific TFM's version is outside the house set (out of support, or an STS), **warn** (print a note) for manual review — don't change it.
- **Normalize the plain-`net` targets to exactly the house set.** Add whichever house TFM is missing, and replace every other plain `net` — an out-of-support release, any STS, `netcoreapp*` — with the set. This fires **only when a plain-`net` target already exists** — a `netstandard`-only library is left untouched (never force `net` onto it).
- **A drop is proposed, never automatic.** In the `old → new` proposal, list each TFM the normalization would remove on its own line with its reason (`drops net8.0 — out of support since 2026-11-10`), apart from the additions, so the user can keep one deliberately; a kept TFM is noted in *Compatibility*.

  Worked examples, with the house set at `net10.0`:

  | before | after |
  |---|---|
  | `netstandard2.0`, `net8.0`, `net10.0` (the pre-2026-11 house set) | `netstandard2.0;net10.0` — drops `net8.0` |
  | `netstandard2.0;net8.0` | `netstandard2.0;net10.0` — drops `net8.0` |
  | `net8.0` | `net10.0` — drops `net8.0` |
  | `net6.0` | `net10.0` — drops `net6.0` |
  | `net9.0` | `net10.0` — drops `net9.0` |
  | `net10.0` | `net10.0` (unchanged) |
  | `netstandard2.0` | `netstandard2.0` (unchanged) |

- When the result carries more than one TFM, use the plural **`<TargetFrameworks>`** element (`;`-separated — `netstandard*` first, then ascending `net`, then any preserved platform TFM), converting from a singular `<TargetFramework>` if needed.
- **Log the change:** record the `old → new` TFM set in the release's `RELEASENOTES.md` *Compatibility* sub-section and update the README **"supported target frameworks"** line. A **dropped** TFM is a breaking change for consumers on it — a library that keeps `netstandard2.0` still installs, but those consumers fall back to that asset and lose any API guarded by a modern TFM. Record it under *Breaking Changes & Migration* as well as *Compatibility*, and print a note when `X.Y.Z` is not a major bump (SemVer treats a dropped TFM as breaking; the version choice stays the user's).

## Release documents

What must be *true* of the released documentation. The bundled templates carry the shape (section order, heading levels, tone, length) so SKILL.md doesn't have to reproduce whole documents — see *Bundled files*. Writing them the first time (the README badge set, the community files) is in `reference/first-release.md`.

### `README.md`

The repository-root README is **packed into the nupkg** (`PackageReadmeFile`) and is the package's nuget.org landing page. [`templates/package-README.md`](templates/package-README.md) carries the section order: title → badges → one-paragraph intro → what's-new callout → *Features* → *Installation* → *Quick start* → *Documentation* → *License*. Keep it **summary-length** — the guides carry the detail.

**Link rule — a correctness constraint, not a style preference.** The README is packed, so it renders on nuget.org, which resolves **no relative link** — not into `docs/`, not to a repo-root file such as `LICENSE.md` or `RELEASENOTES.md`, packed or not: each one renders as an empty `href`.

- **No relative links at all** — name repository files in plain text (`RELEASENOTES.md`, `LICENSE.md`). `RELEASENOTES.md` is not even packed, and nuget.org shows `PackageReleaseNotes` in its own *Release Notes* tab.
- **Absolute links only to stable, non-repository URLs** — the nuget.org package page, and `https://licenses.nuget.org/MIT` for the license.
- **Point at the guides in prose** — name where they live (`docs/guides/`, indexed by `docs/guides/README.md`) and what they cover. **No clickable per-guide links.**
- **No absolute GitHub URLs** — they hard-code org/repo/branch and rot on a rename.

Note the asymmetry: `docs/guides/README.md` is **not** packed, so relative links between the guides are correct *there*. The rule applies to the packed README only.

**What's-new callout** — a single blockquote after the intro:

```markdown
> **What's new in X.Y** — <one-line highlight>. See RELEASENOTES.md in the repository.
```

**Supported target frameworks** — the `Targets **<TFMs>**; built on <primary dependency + version>.` line under *Installation*, updated only when the TFM set moved (see *In-repo edits*).

### `RELEASENOTES.md`

Repo-root, newest-first, one section per release. [`templates/RELEASENOTES.md`](templates/RELEASENOTES.md) carries both variants — **first release** (*Feature overview · Compatibility · Version*) and **subsequent release**.

- **Prepend** the new section above the previous one. If the top section is headed `(unreleased)`, **rename** it to `<Name> vX.Y.Z Release Notes` rather than adding a second block.
- **Sub-sections**, in this order and only where non-empty: *New Features · Fixes · Breaking Changes & Migration · Dependencies · Compatibility · Version*. Match the repo's existing style where it already differs.
- **Dependencies** records every `old → new` transition and any coupled set deliberately held back (see *NuGet package refresh*).
- **Compatibility** records the `old → new` TFM set when it moved; a **dropped** TFM is called out as a compatibility break.

### Guides — `docs/guides/`

One markdown guide per category the library actually has, plus an index at `docs/guides/README.md`. **The count follows the library** — one category, one guide. (Enigma.Core has 13 because it has 13 algorithm categories; that is a consequence of its surface, not a target.)

- **Shape** — [`templates/guide.md`](templates/guide.md) for a guide (intro → supported algorithms/operations table → key types table → `###`-per-scenario usage → notes), [`templates/guides-README.md`](templates/guides-README.md) for the index.
- **Delegation** — guides are independent and split cleanly. Where the running command allows delegation (`/build`; never `/vibe` or `/bulk`), write them **one per sub-agent**, giving each the target path and the relevant public API surface — see [**dev-workflow**'s `reference/build-flow.md`](../dev-workflow/reference/build-flow.md), *Sub-Agent Delegation*; otherwise write them sequentially. Either way the owner integrates and re-verifies every snippet before the phase is done.

**The snippet-verification gate — required** whenever a guide or the README quick-start is touched:

- Cross-check **every API reference in every code fence** against the real public surface in `src/`: `using` namespaces, factory types and their `Create*` methods, service members and their argument shapes (including sync/async and `await`), static helpers, extension methods, enums and options types.
- **Fix any mismatch in place.**
- **Record the coverage in the completion doc as a table** — per file: *snippets · symbols · mismatches · uncertain*, with totals. (Enigma.Core's polish pass recorded 60 snippets / 209 symbols / 0 mismatches; the table is what makes the claim auditable.)

The gate exists because **there is no compile harness for doc snippets** — nothing else catches drift when the API moves. A permanent doc-sample test project is the known alternative; Enigma.Core considered and declined it. It is not required here.

### Community files

- **`SECURITY.md`, `CONTRIBUTING.md`, `LICENSE.md`** — see `reference/first-release.md`.
- **No `CHANGELOG.md`.** `RELEASENOTES.md` is the single release-notes source; a second chronology guarantees divergence. Don't add one, and if the repo has both, say so.
- **`CLAUDE.md`** — a repo-specific agent guide, not a release artifact and not a template. If the repo has one, **dev-workflow**'s documentation-freshness sweep covers it.

## NuGet package refresh

- Run `dotnet list package --outdated` to see what moved.
- Apply the **non-coupled** bumps by editing `<PackageVersion>` entries in `Directory.Packages.props` (see **dotnet-solution-config** for the CPM file's layout).
- **Hold back the version-coupled ecosystems** unless the user opts in — bump each set together, never one package at a time. Which packages form a set is defined once, in **dotnet-solution-config** (*Central Package Management*).
- **Record every `old → new` transition** in the release's `RELEASENOTES.md` section (a *Dependencies* bullet), and note any coupled set deliberately held back.

## Runbook — print, never run

Print the following for the user to run (these are the `docs/RELEASE.md` steps; the bundled template is the fuller checklist). State explicitly: **the skill prints these; the user runs them.**

```bash
# 1. Pre-flight (Release configuration) — the test form per *Detect the specifics*
dotnet build <solution> -c Release
dotnet test --solution <solution> -c Release    # VSTest mode: dotnet test <solution> -c Release

# 2. Merge the release branch into the default (published) branch, then locally:
git switch <default-branch> && git pull

# 3. Tag — match existing tags; default bare X.Y.Z
git tag X.Y.Z
git push origin X.Y.Z

# 4. Pack (GeneratePackageOnBuild is off)
dotnet pack <lib.csproj> -c Release -o ./artifacts

# 5. Push to NuGet (API key has push rights; never commit/echo it)
dotnet nuget push ./artifacts/<PackageId>.X.Y.Z.nupkg \
  --api-key <NUGET_API_KEY> \
  --source https://api.nuget.org/v3/index.json
```

Then **post-publish verification**: the package page shows `X.Y.Z`; the README NuGet badge resolves; `dotnet add package <PackageId> --version X.Y.Z` restores; and the tag exists with notes matching `RELEASENOTES.md`.

Detect the specifics rather than assuming them:

- **Tag format** — `git tag` to see the repo's convention (bare `X.Y.Z` vs. `vX.Y.Z`) and match it; default to **bare `X.Y.Z`** for a repo with no tags.
- **Test form** — `dotnet test --solution <solution>` when the root `global.json` sets `"test": { "runner": "Microsoft.Testing.Platform" }` (the house default, see **xunit-v3**); otherwise (VSTest mode, where `--solution` fails with `MSB1001`) `dotnet test <solution>`. Print only the form that applies.
- **Solution vs. single project** — use the solution file (`.slnx` / `.sln`) for the build/test pre-flight; if the repo has no solution (one packable project), build the library `.csproj` and test the test project — `dotnet test --project <tests csproj>` in MTP mode, `dotnet test <tests csproj>` in VSTest mode — never the library `.csproj` (it holds no tests, and `--solution` rejects a project file). No test project: drop the test line and say so.
- **Default branch** — the published branch you merge into and pack from; the house repos use `main` or `master`. Confirm with `git remote show origin` (or the local default) if unsure.

The merge/tag/push steps assume an initialized git repo with a remote — skip them for a repo that isn't set up to publish yet.

## App vs library

For a **non-packable app** (no `PackageId`, not published to NuGet), skip the pack/push steps entirely — the version bump, `RELEASENOTES.md`, README callout, and the tag still apply. For an app you also **offer to generate an MSI profile** — read [`reference/msi-profiles.md`](reference/msi-profiles.md) before offering it.

## The shape of a release work item

**dev-workflow** owns phases, plan files and completion records; this skill owns what goes in them for a release. Two shapes:

- **Routine release — a single phase:** version, notes, callout, dependency refresh, runbook.
- **First release — four phases**, in an order two constraints fix: see `reference/first-release.md`.

## Cross-references

- **dev-workflow** — a release is its own `FEATURE-HHHH` work item (see *The shape of a release work item*); dev-workflow owns branch naming, the never-commit-myself rule, tag/publish ownership, the `docs/roadmap.md` + `docs/plan/` + `docs/done/` records, and the doc-freshness sweep.
- **dotnet-solution-config** — the CPM `Directory.Packages.props` file this skill edits when refreshing dependency versions, and the coupled-ecosystem rule.
- **dotnet-solution-setup** — owns the dated house TFM policy (*Target frameworks*): the set new projects target and the set this skill's release-time normalization proposes.
- **git-repo-hygiene** — `.gitignore` / `.gitattributes` / line-ending normalization.

## Bundled files

- [`reference/first-release.md`](reference/first-release.md) — the first release: its steps and work-item shape, the 12 packaging properties and the symbols rule, the license audit, the README badge set and the community files.
- [`reference/msi-profiles.md`](reference/msi-profiles.md) — app MSI profiles: the GUID contract, location and filenames, first and subsequent profiles, the field reference.
- [`templates/RELEASE.md`](templates/RELEASE.md) — the human release checklist (pre-flight → merge → tag → pack → push → verify). Offer it into the target repo's `docs/RELEASE.md` and fill its placeholders (`{{PACKAGE_ID}}`, `{{SOLUTION}}`, `{{LIB_CSPROJ}}`, `{{LIB_DIR}}`, `{{DEFAULT_BRANCH}}`).
- [`templates/msiprofile.template.json`](templates/msiprofile.template.json) — the MSI-profile skeleton, **apps only**: see `reference/msi-profiles.md`.
- [`templates/package-README.md`](templates/package-README.md) — the packed root `README.md` (section order: *Release documents*).
- [`templates/RELEASENOTES.md`](templates/RELEASENOTES.md) — the root `RELEASENOTES.md`, both variants.
- [`templates/guide.md`](templates/guide.md) — one per-category guide under `docs/guides/`.
- [`templates/guides-README.md`](templates/guides-README.md) — the `docs/guides/README.md` index: themed groups of relative links (repo-only, never packed).
- [`templates/SECURITY.md`](templates/SECURITY.md) — the root `SECURITY.md`: supported versions, GitHub private vulnerability reporting, what to expect, scope.

Every doc template, `RELEASE.md` included, follows one handling rule: **create only if missing — diff against an existing file, never clobber it.** An empty target (0 bytes or whitespace only — such as the `README.md` / `RELEASENOTES.md` placeholders **dotnet-solution-setup** creates at bootstrap) counts as missing: fill it from the template.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Auto-pushing to NuGet, or running `git tag` / `dotnet pack` / `dotnet nuget push` for the user | The skill only prints them; the user runs the outward-facing commands. |
| Bumping one package of a version-coupled set individually | Bump the set (dotnet-solution-config) together, or hold the whole set back. |
| Forgetting `<PackageReleaseNotes>` in the library csproj | Add it, mirroring the top of `RELEASENOTES.md`. |
| Tagging with the wrong prefix (bare vs. `v`) | Detect existing tags and match; default bare `X.Y.Z`. |
| Skipping the Release-config build/test pre-flight | Always `dotnet build <solution> -c Release` and `dotnet test` with `-c Release` before tagging — `--solution <solution>` in MTP mode, positional `<solution>` in VSTest mode (*Detect the specifics*). |
| Not logging `old → new` dependency transitions | Record every version change (and held-back set) in `RELEASENOTES.md`. |
| TFM set changed but the README "supported target frameworks" line / `RELEASENOTES.md` *Compatibility* note not updated | Log the `old → new` TFM set and keep the audit trail in sync; flag a dropped TFM as a breaking change. |
| Committing or echoing the NuGet API key | The key is a secret — it never appears in the repo or output. |
| A relative link in the packed README — `docs/…`, `LICENSE.md`, `RELEASENOTES.md` | Dead on nuget.org: every relative link renders as an empty `href`. Name files in plain text, link the license to `https://licenses.nuget.org/MIT`, point at the guides in prose. |
| Adding a `CHANGELOG.md` alongside `RELEASENOTES.md` | One release-notes source only; two chronologies diverge. `RELEASENOTES.md` wins. |
| Shipping a guide whose snippets were never verified against `src/` | Run the snippet-verification gate and record the coverage table — there is no compile harness to catch drift. |
| Packing but never inspecting the artifact | Pack-verify into a throwaway dir and check version, embedded non-empty README, LICENSE, the nuspec fields and dependency floors — then delete it. |

If the target repo already has its own release conventions (tag prefix, notes layout, badge set), stay consistent with them and flag the divergence rather than silently imposing these defaults.
