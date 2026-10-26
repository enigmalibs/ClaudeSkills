**Status:** DONE
**Type:** FEATURE
**Branch:** feature/feature-f1bc-readme
**Run:** feature/2026-10-26-readme-documentation

# FEATURE-F1BC — README documentation

## Objective

Replace the one-line `README.md` stub (`# ClaudeSkills`) with documentation that tells a newcomer what the repository is, how to install it into Claude Code, how the slash commands work together, and what each skill covers.

## Context & constraints

- The repository distributes Claude Code content: 5 slash commands under `commands/` (`/interview`, `/build`, `/vibe`, `/bulk`, `/review`) and 17 skills under `skills/<name>/SKILL.md` (workflow, .NET/Avalonia/WPF stack, tooling).
- The only executable code is `skills/dev-workflow/scripts/roadmap.py` (Python 3 stdlib) with its unittest suite `test_roadmap.py` (46 tests, `python3 -B -m unittest discover -s skills/dev-workflow/scripts`).
- No `LICENSE`, no CI, no build system. Remote: `https://github.com/enigmalibs/ClaudeSkills.git`.
- Every command has `disable-model-invocation: true` — it runs only when the user types it.
- Commands load skills by name (`dev-workflow`, `vibe-workflow`, `review-standards`, plus stack skills), so the two must be installed together.

## Decisions

See *Decisions taken autonomously* below; the README is a single file at the repository root, in English, with ASCII diagrams and padded tables.

## Phase — single

### Steps

1. Write `README.md` with these sections, in order:
   1. Title + one-paragraph summary.
   2. **What's inside** — counts and the repository layout tree.
   3. **Installation** — prerequisites, clone, user scope (`~/.claude/`) and project scope (`.claude/`), symlink for bash and PowerShell, copy fallback, update and uninstall.
   4. **The dev workflow** — the planning/building split, the ASCII flow between commands, the `docs/roadmap.md` / `docs/plan/` / `docs/done/` artifacts, work-item IDs, branch naming.
   5. **Commands** — one table (command · argument · what it does · writes/commits), then a short subsection per command.
   6. **Skills** — catalogue tables grouped as Workflow, .NET & desktop stack, Tooling; each row a link to its `SKILL.md` and a one-line summary.
   7. **Maintaining this repository** — conventions for a skill/command file (frontmatter, `**Version:**` line), running the `roadmap.py` tests.
2. Keep every table column-aligned (readable raw), and every relative link pointing at a file that exists.

### Acceptance criteria

- `README.md` covers all seven sections above.
- Every one of the 5 commands and 17 skills present in the repository appears in the README; no command or skill is named that does not exist.
- Every relative link in the README resolves to an existing file or directory.
- Every Markdown table in the README is column-aligned (each `|` at the same offset on every line of the table).
- The documented test command runs green.
- No license is claimed; no remote-script installation (`curl | bash`) is suggested.

## Out of scope

- Adding a `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md` or CI.
- Changing any command or skill file.
- Per-skill documentation pages or a docs site.
- Line-ending normalization.

## Decisions taken autonomously

| Question                         | Chosen                                                                              | Why                                                                                     | Alternatives rejected                                    |
|----------------------------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|----------------------------------------------------------|
| README scope                     | Overview, install, workflow guide, command + skill catalogue, maintenance           | A newcomer needs the what, the how-to-install and how the commands fit together         | Minimal install-only README; exhaustive per-skill manual |
| One file or a docs site          | Single root `README.md`                                                             | Skills are already self-documenting; a docs site is new infrastructure nobody asked for | `docs/` site; per-skill README files                     |
| Install method                   | `git clone`, then symlink (copy as fallback); user or project scope                 | Symlinks keep installs current with `git pull`; matches how the author installs them    | Plugin/marketplace packaging; copy-only                  |
| Shells covered                   | bash and PowerShell                                                                 | The house targets Windows (WPF, `py -3` in `roadmap.py`) as well as Linux/macOS         | bash only                                                |
| Install granularity              | Everything recommended; workflow skills required by commands; stack skills optional | Commands load skills by name — a missing `dev-workflow` breaks `/build`                 | Leave it to the reader                                   |
| Workflow diagram                 | ASCII in a code block                                                               | House style (`vibe-workflow` §3); identical raw and rendered                            | Mermaid; image                                           |
| Version numbers in the catalogue | Not listed; point at each file's `**Version:**` line                                | Versions move with nearly every edit; a copy in the README would go stale               | A version column                                         |
| License section                  | Omitted; no license claimed                                                         | There is no `LICENSE` file and picking terms is the owner's call; follow-up recorded    | Inventing an MIT section                                 |
| Maintenance section              | Short: file conventions, version bump, `roadmap.py` tests                           | The only real maintenance tasks the repo has                                            | No maintenance section; full CONTRIBUTING guide          |
| Language                         | English                                                                             | All repository content is English                                                       | French                                                   |
