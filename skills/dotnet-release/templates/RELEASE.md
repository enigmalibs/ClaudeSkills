<!--
  Release runbook template. Copy into the target repo as docs/RELEASE.md (create only if missing)
  and fill the placeholders:
    {{PACKAGE_ID}}   NuGet package id                 e.g. Enigma.Cryptography
    {{SOLUTION}}     solution file                    e.g. Enigma.Cryptography.slnx
    {{LIB_CSPROJ}}   packable library project path    e.g. src/Enigma.Cryptography/Enigma.Cryptography.csproj
    {{LIB_DIR}}      packable library directory       e.g. src/Enigma.Cryptography/
    {{DEFAULT_BRANCH}} default/published branch       e.g. main or master
  Tag form: match the repo's existing `git tag`s; default to bare X.Y.Z when the repo has none.
-->
# Release runbook

Reusable checklist for publishing a new **{{PACKAGE_ID}}** version to NuGet. Only the packable library
project (`{{LIB_DIR}}`) is published; any Tools / CLI / Desktop projects in the solution ship as source.

Replace `X.Y.Z` with the version being released (e.g. `1.2.0`) throughout. The version lives in
`{{LIB_CSPROJ}}` (`<Version>`); a CLI or app in the same solution may carry its own independent `<Version>`
and is not published to NuGet.

## 1. Pre-release checks

Run from the repository root, on the branch that will be merged:

- [ ] `<Version>X.Y.Z</Version>` set in `{{LIB_CSPROJ}}`.
- [ ] `RELEASENOTES.md` has a top `X.Y.Z` section describing the release (newest-first; any `(unreleased)`
      heading renamed to `X.Y.Z`).
- [ ] `<PackageReleaseNotes>` in the library csproj summarizes the release and points to `RELEASENOTES.md`.
- [ ] README badges and the "what's new" callout reflect `X.Y.Z`.
- [ ] `<TargetFrameworks>` reflect the house TFM set (dotnet-solution-setup, *Target frameworks*; `netstandard*` preserved); any change was proposed/confirmed and logged in `RELEASENOTES.md` *Compatibility* — a dropped TFM also under *Breaking Changes & Migration*.
- [ ] Clean, warning-free build across all TFMs:
      ```bash
      dotnet build {{SOLUTION}} -c Release
      ```
- [ ] Full test suite green:
      ```bash
      dotnet test --solution {{SOLUTION}} -c Release
      # If the test apphost can't find the runtime, prefix: DOTNET_ROOT=~/.dotnet
      ```
- [ ] README samples and any CLI reference verified against the built version.

## 2. Merge to the default branch

Merge the release branch into the default (published) branch — `{{DEFAULT_BRANCH}}` — via a pull request (or
fast-forward), then check it out locally:

```bash
git switch {{DEFAULT_BRANCH}}
git pull
```

## 3. Tag the release

Match the repo's existing tag convention — run `git tag` to see how prior releases were tagged (bare `X.Y.Z`
vs. `vX.Y.Z`). Default to a **bare** `X.Y.Z` tag when the repo has none. Tag the merge commit and push the tag:

```bash
git tag X.Y.Z
git push origin X.Y.Z
```

## 4. Pack

`GeneratePackageOnBuild` is **off** for this library, so no `.nupkg` is produced on an ordinary build — pack
explicitly in Release to get the artifact you publish:

```bash
dotnet pack {{LIB_CSPROJ}} -c Release -o ./artifacts
```

This writes `./artifacts/{{PACKAGE_ID}}.X.Y.Z.nupkg` — and nothing else; a `.snupkg` beside it means the
symbol opt-in crept back into the csproj. Confirm the version in the filename matches the tag, and
(optionally) inspect the package contents — it should bundle `README.md` and `LICENSE.md` and declare the
expected dependency floors.

## 5. Push to NuGet

Publish with a NuGet API key that has push rights for the `{{PACKAGE_ID}}` package:

```bash
dotnet nuget push ./artifacts/{{PACKAGE_ID}}.X.Y.Z.nupkg \
  --api-key <NUGET_API_KEY> \
  --source https://api.nuget.org/v3/index.json
```

`dotnet pack` produces **only** the `.nupkg` — that single file is what gets pushed. This project does not
ship a `.snupkg` symbols package: the symbol opt-in properties (`IncludeSymbols`,
`SymbolPackageFormat`) are deliberately absent from the csproj and must stay that way, and `pack` is never
run with `--include-symbols`. The API key is a secret — never commit or echo it.

## 6. Post-publish verification

- [ ] The package page shows the new version: <https://www.nuget.org/packages/{{PACKAGE_ID}}> (indexing can
      take a few minutes).
- [ ] The README NuGet badge resolves to `X.Y.Z` (shields.io caches briefly).
- [ ] A scratch project can restore the new version:
      ```bash
      dotnet add package {{PACKAGE_ID}} --version X.Y.Z
      ```
- [ ] The GitHub release/tag is present and its notes match `RELEASENOTES.md`.
