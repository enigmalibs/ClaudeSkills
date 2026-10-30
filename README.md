# ClaudeSkills

House slash commands and skills for [Claude Code](https://claude.com/claude-code): a plan-then-build development workflow with a persistent roadmap, an autonomous "plan and build it unattended" mode, a .NET code review, and the .NET / Avalonia / WPF conventions those commands apply when they write code.

## What's inside

- **5 slash commands** — `/interview`, `/build`, `/vibe`, `/bulk`, `/review` — that you run by typing them.
- **17 skills** — instructions Claude loads on demand: 3 workflow skills the commands depend on, 11 .NET and desktop convention skills, and 3 tooling skills.
- **`roadmap.py`** — a standard-library Python script that keeps the roadmap table and statuses consistent.

```
ClaudeSkills/
├── commands/                    slash commands  → ~/.claude/commands/
│   ├── interview.md
│   ├── build.md
│   ├── vibe.md
│   ├── bulk.md
│   └── review.md
├── skills/                      skills          → ~/.claude/skills/
│   ├── dev-workflow/
│   │   ├── SKILL.md
│   │   ├── reference/build-flow.md
│   │   └── scripts/roadmap.py   (+ test_roadmap.py)
│   ├── vibe-workflow/
│   ├── review-standards/
│   └── …                        one folder per skill, SKILL.md plus optional
│                                reference/, templates/, scripts/
└── docs/                        this repository's own roadmap, plans and
                                 completion records (the workflow, applied to itself)
```

## Installation

### Prerequisites

- [Claude Code](https://claude.com/claude-code) and `git`.
- Python 3 for `roadmap.py` and the `html-report` build script (`python3`, or `py -3` on Windows). Optional for the workflow, which then edits the roadmap by hand; required by `html-report`.
- The .NET SDK for the .NET skills and `/review`.

### Install for every project (user scope)

Clone the repository once, then link its commands and skills into `~/.claude/`. Links let a `git pull` update everything in place.

```bash
git clone https://github.com/enigmalibs/ClaudeSkills.git ~/src/ClaudeSkills
REPO=~/src/ClaudeSkills
mkdir -p ~/.claude/commands ~/.claude/skills
for f in "$REPO"/commands/*.md; do ln -sfn "$f" ~/.claude/commands/; done
for d in "$REPO"/skills/*/;     do ln -sfn "${d%/}" ~/.claude/skills/; done
```

On Windows (PowerShell; symbolic links need Developer Mode or an elevated shell):

```powershell
git clone https://github.com/enigmalibs/ClaudeSkills.git "$HOME\src\ClaudeSkills"
$repo = "$HOME\src\ClaudeSkills"
New-Item -ItemType Directory -Force "$HOME\.claude\commands", "$HOME\.claude\skills" | Out-Null
Get-ChildItem "$repo\commands\*.md" | ForEach-Object {
    New-Item -ItemType SymbolicLink -Force -Path "$HOME\.claude\commands\$($_.Name)" -Target $_.FullName }
Get-ChildItem "$repo\skills" -Directory | ForEach-Object {
    New-Item -ItemType SymbolicLink -Force -Path "$HOME\.claude\skills\$($_.Name)" -Target $_.FullName }
```

Both scripts **replace** an existing command or skill of the same name. Prefer copies to links? `cp "$REPO"/commands/*.md ~/.claude/commands/ && cp -r "$REPO"/skills/* ~/.claude/skills/` (or `Copy-Item -Recurse`) — then re-copy to update.

Start a new Claude Code session afterwards: the commands appear in the `/` menu, and skills load when a task matches their description.

### Install for one project (project scope)

Copy the folders you need into the project's `.claude/commands/` and `.claude/skills/`, and commit them so the whole team gets them. Use copies here, not links — a link to your own clone does not exist on a teammate's machine.

### What to install

Install the commands and skills **from the same checkout**. Each command loads skills by name — `/interview` and `/build` need `dev-workflow`, `/vibe` and `/bulk` also need `vibe-workflow`, `/review` needs `review-standards` — and they evolve together. The stack and tooling skills are optional; without them the commands still run, just without those conventions.

### Update and uninstall

```bash
git -C ~/src/ClaudeSkills pull                       # linked installs update in place;
                                                     # re-run the link loops to pick up new skills
find ~/.claude/commands ~/.claude/skills -maxdepth 1 -type l -lname "$HOME/src/ClaudeSkills/*" -delete
                                                     # uninstall: removes only the links into the clone
```

## The dev workflow

Work is **planned first and built later**. Planning produces a plan file that is the contract for the build; building turns one plan into tested code on its own branch.

```
                      /review  (.NET only, read-only)
                         |  docs/review/<date>-<scope>.md
                         v
  spec draft -----> /interview -----> docs/roadmap.md + docs/plan/<ID>.md   (TODO)
      |             asks you, plans          |
      |                                      +--> /build <ID>     one dev at a time; you commit
      |                                      +--> /bulk [<ID>…]   every TODO dev, unattended
      |
      +-----------> /vibe  ---------> plans *and* builds unattended on a run branch
                    answers its own interview
```

### What it writes in your project

| Path                      | Holds                                                                                          |
|---------------------------|------------------------------------------------------------------------------------------------|
| `docs/roadmap.md`         | One aligned table of every work item: ID · Title · Status · Plan. Row order is priority order. |
| `docs/plan/<ID>.md`       | The full plan of one item: objective, decisions, phases, acceptance criteria.                  |
| `docs/done/<ID>.md`       | One completion record per finished dev: summary, files touched, deviations, build/test proof.  |
| `docs/review/<date>-*.md` | A `/review` report (plus an `.html` rendering).                                                |

- **Work items** are `FEATURE-HHHH`, `BUG-HHHH` or `CODE-REVIEW-HHHH`, where `HHHH` is random hex (`FEATURE-3A7F`). A large item is split into phases — `FEATURE-3A7F-PHASE01`, `-PHASE02`, … — and a code review gets one phase per finding, most severe first.
- **A dev** is one deliverable: a single-phase item or one phase. Each dev gets its own branch, cut from your current `HEAD` (never from the default branch): `feature/feature-3a7f-phase01-<slug>`, `bugfix/bug-9c2e-<slug>`, `review/code-review-7f10-<slug>`.
- **Statuses** are `TODO`, `IN PROGRESS`, `DONE` and `ABANDONED`. Dropped items are never deleted: they become `ABANDONED` with a footnote saying why. A multi-phase item's row follows its phases; abandoning the item abandons every phase still open.
- **Definition of Done**: the build adds no warning and the test suite no failure beyond the **baseline** taken before the dev's first change (a clean baseline means zero warnings and every test passing, new tests included), every acceptance criterion is met, the statuses are updated, and the completion record is written. Pre-existing warnings and failures are left alone and listed in the record as follow-ups.
- **Commits** follow conventional commits scoped by the base ID: `feat(FEATURE-3A7F): add login flow (PHASE01)`, `fix(BUG-9C2E): …`, `docs(roadmap): plan …`.

The full rules live in [`skills/dev-workflow/SKILL.md`](skills/dev-workflow/SKILL.md) and its [build-flow reference](skills/dev-workflow/reference/build-flow.md).

### Typical flows

- **Plan together, build step by step** — `/interview <spec>`, commit the plan, then `/build` and commit after each dev.
- **Plan together, build unattended** — `/interview <spec>`, commit the plan, then `/bulk`; review and merge the run branch.
- **Hands-off** — `/vibe <spec>`; review and merge the run branch.
- **From a code review** — `/review`, then `/interview @docs/review/<date>-<scope>.md` (or `/vibe @…`) to turn its findings into a `CODE-REVIEW` item.

## Commands

All five commands set `disable-model-invocation: true`: they run only when you type them, never on Claude's own initiative.

| Command      | Argument                          | Does                                                  | Git                                                           |
|--------------|-----------------------------------|-------------------------------------------------------|---------------------------------------------------------------|
| `/interview` | `<spec draft>`                    | Interviews you, then writes roadmap rows + plan files | Writes on your current branch; never commits                  |
| `/build`     | `[<ID>]`                          | Implements one planned dev to the Definition of Done  | Cuts the dev branch; prints the commit message for you to run |
| `/vibe`      | `[<spec draft>]`                  | Plans a spec itself, then builds every dev            | Commits and merges on a run branch; never pushes              |
| `/bulk`      | `[<ID>…]`                         | Builds already-planned `TODO` items unattended        | Commits and merges on a run branch; never pushes              |
| `/review`    | `[<ID>… \| <path> \| scope text]` | Reviews a .NET solution against the house skills      | Read-only; writes two report files under `docs/review/`       |

### `/interview` — plan with you

Classifies the draft as a `FEATURE`, `BUG` or `CODE-REVIEW`, explores the codebase, then asks its questions in rounds — highest impact first, each with a recommended option. Every rule of the house skills is applied rather than asked. It prints a consolidated summary, writes the roadmap rows and plan files at `TODO`, and suggests a `docs(roadmap): plan …` commit. **It never implements.** Answer "go with your recommendations" at any point to converge quickly.

### `/build` — build one planned dev

With an ID, builds that item's next `TODO` / `IN PROGRESS` phase (or the given phase). Without one, it prints the roadmap with the recommended item marked and asks which ID to build. An item or phase already `DONE` or `ABANDONED` is never rebuilt. It sanity-checks the plan against the code and stops to ask if they have drifted. Then it takes the build/test baseline, branches, implements, meets the Definition of Done, offers to refresh any user-facing docs the change made stale, and prints the commit message. **You commit**; then run `/build` again for the next dev. It also finishes a dev that `/vibe` or `/bulk` quarantined.

### `/vibe` and `/bulk` — unattended runs

`/vibe <spec>` answers its own interview with the options it would have recommended (recording each decision in the plan) and builds the result. `/bulk` builds items that `/interview` already planned: every unowned `TODO` row, or the base IDs you pass. Both:

- work on a **run branch** `<feature|bugfix|review>/<yyyy-mm-dd>-<slug>` cut from your current `HEAD`, and fast-forward each dev into it (`--ff-only`, falling back to `--no-ff` only if the run branch moved), so it stays linear — the planning or claim commit, then one commit per dev — and reads as one bubble once you merge it;
- take **one build/test baseline per run**, before the first dev, and measure every dev against it;
- **never push**, never write to the branch you started from or to the default branch, and add no attribution trailer to their commits;
- give each dev at most **3 fix cycles**; a dev still red after that is **quarantined** (its branch left unmerged, a roadmap footnote explains why) and the run moves on — finish it later with `/build <ID>`;
- end with a report listing every dev and the commands to review, merge and clean up;
- **resume** a run cut short: re-run the command with no argument from the run branch.

They need a permission mode that does not prompt for file writes and `git commit` (auto mode, or an allowlist), and refuse to start in plan mode or on a dirty working tree.

### `/review` — .NET code review

Builds and tests the solution as a baseline (`dotnet test --solution` when `global.json` selects the Microsoft Testing Platform runner, the positional form in VSTest mode), then reviews the whole solution, a path, or the code of the work items you name — their commits in `HEAD`'s history. It checks SOLID, XAML, logging, exceptions, async, MVVM, tests, security, style and performance against the house skills, and writes `docs/review/<yyyy-mm-dd>-<scope>.md` plus an HTML rendering. Findings carry a severity (Critical → Low), their locations and a recommended fix. It is read-only otherwise, and its report is the input `/interview` and `/vibe` turn into a `CODE-REVIEW` item. Add "use sub-agents" to the argument for a parallel review.

## Skills

Skills load automatically when a task matches their description, or when a command loads them. Each `SKILL.md` is the reference; the summaries below are a map.

### Workflow

| Skill                                                  | Covers                                                                                                   |
|--------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| [`dev-workflow`](skills/dev-workflow/SKILL.md)         | Roadmap, plan and completion-doc formats, work-item IDs, branch naming, Definition of Done, `roadmap.py` |
| [`vibe-workflow`](skills/vibe-workflow/SKILL.md)       | Autonomy overrides for `/vibe` and `/bulk`: run branch, own commits, fix budget, quarantine, resume      |
| [`review-standards`](skills/review-standards/SKILL.md) | Severity scale, review dimensions, finding and report shapes, checklists and templates for `/review`     |

### .NET and desktop conventions

| Skill                                                                  | Covers                                                                                                      |
|------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| [`dotnet-solution-setup`](skills/dotnet-solution-setup/SKILL.md)       | New-solution bootstrap checklist, csproj conventions, target frameworks, startup and hosting; templates     |
| [`dotnet-solution-config`](skills/dotnet-solution-config/SKILL.md)     | Root `.editorconfig`, `Directory.Build.props`, `Directory.Packages.props` (central packages), `global.json` |
| [`dotnet-di-design`](skills/dotnet-di-design/SKILL.md)                 | Constructor injection, abstractions, static vs injected helpers, service lifetimes and registration         |
| [`dotnet-async`](skills/dotnet-async/SKILL.md)                         | `Task` APIs, cancellation, background work in hosted apps, updating UI state from background threads        |
| [`csharp-extension-methods`](skills/csharp-extension-methods/SKILL.md) | When a helper should be an extension method, written as C# 14 extension blocks                              |
| [`communitytoolkit-mvvm`](skills/communitytoolkit-mvvm/SKILL.md)       | ViewModels with CommunityToolkit.Mvvm, written explicitly — no source-generator attributes                  |
| [`avalonia`](skills/avalonia/SKILL.md)                                 | Avalonia 12 apps: packages, IHost/DI bootstrapping, XAML bindings, views and ViewModels, app lifetime       |
| [`wpf`](skills/wpf/SKILL.md)                                           | WPF apps: project setup, `App.xaml` wiring, IHost/DI integration, resolving windows and ViewModels          |
| [`enigma-avalonia-desktop`](skills/enigma-avalonia-desktop/SKILL.md)   | The Enigma.Avalonia.Desktop control library: navigation, ribbon, docking, editors, dialogs, data, theming   |
| [`enigma-icons-avalonia`](skills/enigma-icons-avalonia/SKILL.md)       | The Enigma.Icons.Avalonia library: the `ei:Icon` control, markup extensions, Phosphor icons, custom sets    |
| [`xunit-v3`](skills/xunit-v3/SKILL.md)                                 | xUnit v3 test projects: layout and naming, packages, `dotnet test`, theories, fixtures, async lifecycle     |

### Tooling

| Skill                                                  | Covers                                                                                                        |
|--------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| [`dotnet-release`](skills/dotnet-release/SKILL.md)     | A NuGet release as a work item: version bump, release docs from templates, pack/tag/push runbook, MSI profile |
| [`git-repo-hygiene`](skills/git-repo-hygiene/SKILL.md) | `.gitignore`, `.gitattributes` and a minimal `.editorconfig` for .NET repos; fixing CRLF/LF churn             |
| [`html-report`](skills/html-report/SKILL.md)           | Self-contained HTML reports from a bundled template: build script, component catalogue, themes, print and PDF |

## Maintaining this repository

- **A command** is `commands/<name>.md`: frontmatter with `description`, `argument-hint`, `disable-model-invocation: true` and `metadata.version`, then the prompt.
- **A skill** is `skills/<name>/SKILL.md`: frontmatter with `name` (the folder name), `description` — the text Claude matches tasks against, so keep it precise — and `metadata.version`, then the instructions. Supporting files go in `reference/`, `templates/` or `scripts/` beside it.
- **Versions** are semantic, in the frontmatter (`metadata:` → `version: "10.2.0"`) — never in the body or the command's output. Bump with every change: patch for a fix or rewording, minor for new or changed behaviour, major for a breaking one. `/review` reads them from disk to name its rulebook in the report.
- **Keep commands and skills in step**: a command refers to skills, sections and scripts by name, so rename them together.
- **Test the scripts** after changing them — `roadmap.py`, and `html-report`'s `new_report.py`:

  ```bash
  python3 -B -m unittest discover -s skills/dev-workflow/scripts      # Windows: py -3 -B -m unittest …
  python3 -B -m unittest discover -s skills/html-report/scripts
  ```
