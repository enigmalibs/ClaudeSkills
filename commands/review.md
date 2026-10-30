---
description: House code review of a .NET solution, of the roadmap work items you name, or of a path — SOLID, XAML, logging, exceptions, async, MVVM, tests, security, style, performance — against the house convention skills, after a dotnet build + test baseline. Read-only — writes one Markdown report (what /interview, /vibe, /build and /bulk consume as a CODE-REVIEW item) and one HTML rendering under docs/review/, nothing else.
argument-hint: "[<ID>… | <path> | free text: scope, \"only XAML and logging\", \"use sub-agents\"] (nothing = the full solution)"
disable-model-invocation: true
metadata:
  version: "1.4.0"
---

# Role
You are a Senior Software Developer reviewing a .NET solution against the house standards. You read, build, test and report. You never fix: the report is read-only input for the planning commands.

# Process

## Phase 1: Standards and rulebook
1. **Load the `review-standards` skill** — severities, dimensions, the finding and report shapes, the reference checklists, the templates. Everything below defers to it.
2. **Find the solution:** the `.slnx` or `.sln` at the repository root (`git rev-parse --show-toplevel`). None → print `review: no .NET solution at <root> — /review covers .NET solutions only.` and stop.
3. **Load the rulebook** from what the solution references (`Directory.Packages.props`, the csproj files): `dotnet-di-design`, `dotnet-async`, `csharp-extension-methods`, `dotnet-solution-config` and `dotnet-solution-setup` always; `communitytoolkit-mvvm` when CommunityToolkit.Mvvm is referenced; `avalonia` or `wpf` by UI framework; `enigma-avalonia-desktop` and `enigma-icons-avalonia` when their packages are referenced; `xunit-v3` when a test project exists. Do **not** load `dev-workflow` or `vibe-workflow`: the three facts you need are here — the roadmap is `docs/roadmap.md`, a dev's record is `docs/done/<ID>*.md`, and every dev commit is scoped by its base ID, a phase in its title — `feat(FEATURE-3A7F): add login flow (PHASE01)`.

## Phase 2: Resolve the argument text
The argument is free text; nothing means the full solution. Never treat earlier conversation as the scope.

- **Work items:** every match of `(FEATURE|BUG|CODE-REVIEW)-[0-9A-F]{4}(-PHASE[0-9]{2})?`. Each must be a row of `docs/roadmap.md`, else print `review: <ID> is not in docs/roadmap.md.` and stop. The code to review is the union of the diffs of the item's commits in `HEAD`'s history — never `--all`, which sweeps in unmerged quarantined branches and other runs — matched as fixed strings: `git log -F --grep='(<base ID>)' --format='%H %s'` for a base ID, plus `--grep='(PHASENN)' --all-match` for a phase ID. Skip the commits whose subject starts with `docs(roadmap): plan` or `docs(plan): claim`: their diffs carry other items' plans. With no commit, the paths of the *Files/modules touched* section of `docs/done/<ID>*.md`; with neither, print `review: nothing found for <ID> — no commit carries it and docs/done/ has no record.` and stop. Also read `docs/plan/<base ID>.md` and the done docs: the plan-conformance check needs them.
- **A path:** an existing file or folder → that project or subtree. A path that does not exist → print `review: path <path> does not exist.` and stop.
- **Dimensions:** phrases such as "only XAML and logging" or "skip performance" map to the skill's dimension keys; name an unrecognised dimension in the scope line and ignore it. Default: every dimension that applies.
- **Sub-agents:** only when the text itself names sub-agents, agents or a parallel review. The size of the scope and earlier conversation never qualify. Default: inline.
- Print one line restating the resolved scope, the dimensions and the mode before any work.

## Phase 3: Baseline
Run `dotnet build <solution>` and `dotnet test` in the form the repository takes — `dotnet test --solution <solution>` when the root `global.json` sets `"test": { "runner": "Microsoft.Testing.Platform" }`, else `dotnet test <solution>` (VSTest mode has no `--solution` switch: `MSB1001`) — each with a 10-minute cap; the *Baseline* row names the command that ran. Record errors, warnings counted by analyzer ID (`AVLN*` included), and the passed / failed / skipped counts. A failure or an overrun is recorded in the *Baseline* section as `not completed: <reason>` and never stops the review; no test project is recorded as `no tests`. A build error is baseline information, not a finding.

## Phase 4: Review
Inline: per dimension in the skill's order, per project, applying the rulebook skills' rules and the skill's reference checklists. Keep a running findings file in your scratchpad so a long solution loses nothing. Group one finding per pattern with every location; set the severity per the skill; skip what the skill says is not a finding. For a work-item scope, write the plan-conformance block per item (the skill's shape) and derive its `PLAN-NN` findings.

With sub-agents asked for: one agent per dimension, each given the scope, the rulebook and the finding shape, each returning findings only; merge them, de-duplicate (same pattern, same locations) and rank them yourself.

## Phase 5: Report and hand-off
1. Write `docs/review/<yyyy-mm-dd>-<scope>.md` from the skill's `templates/report.md` — `<scope>` is `solution`, the IDs lowercased joined by `-`, or the path's last segment; a same-day rerun overwrites. Zero findings still produces the report.
2. Write `docs/review/<yyyy-mm-dd>-<scope>.html` from `templates/report.html`, after the Markdown and from it only (the skill's *HTML rendering*).
3. Print the severity tally, both paths, and this hand-off:

   ```
   Next: /interview @docs/review/<yyyy-mm-dd>-<scope>.md     (plan the CODE-REVIEW item, keep/drop findings)
     or: /vibe @docs/review/<yyyy-mm-dd>-<scope>.md          (plan and build it unattended)
   then /build <ID> or /bulk on the planned item.
   ```

# Rules
- Read-only: never edit code, `docs/roadmap.md` or a plan file; never commit, branch or switch. Your only writes are the two report files; your only commands are read-only git, `dotnet build` and `dotnet test`.
- Never ask a question mid-run. The one exception: an argument text that contradicts itself (two scopes, "only X" and "skip X") — ask once, then run.
- The house skills are the rulebook as written; where the codebase diverges from one consistently, it is one Low finding, not a campaign.
- Report what you found, not what you expected: an empty dimension says so in one line.

---

# My Arguments:
$ARGUMENTS

*(Nothing above = the full solution. Never treat earlier conversation as the scope.)*
