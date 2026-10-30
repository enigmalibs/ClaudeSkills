# Build flow — dev-workflow reference

Read this before building a dev (`/build`, `/vibe`, `/bulk`). The core `SKILL.md` still applies — IDs, the roadmap and `scripts/roadmap.py`, plan files, completion docs, branch names, commit-message formats.

Hard rules: **branch from the current `HEAD`, never from the default branch** · **never mark a dev `DONE` with a failing build or a failing test the baseline did not have** · on a dirty tree, an existing branch name (a quarantined dev's excepted) or no repository, stop and ask.

## Building a dev

- **Create the dev's branch from your current `HEAD`** — the branch or commit it points at; a detached `HEAD` is fine (branch from that commit; the user manages their own git state). Never switch to, or assume, the default branch (`main`/`master`). Name the branch per the core *Version Control*. First check the tree is clean (`git status --porcelain` prints nothing). If the tree is dirty, a branch with that name already exists, or the project has no git repository yet, stop and ask the user before proceeding. The one exception: a quarantined dev — a roadmap footnote names its branch as unmerged — is finished on that existing branch (`/build`'s *Quarantined dev*).
- Branch first, then plan: on the new branch the first change is the item's roadmap row and plan file, created at `IN PROGRESS` (`roadmap.py add <ID> "<title>" [--phase …] --status "IN PROGRESS"`), when they don't exist yet — or, when they were planned earlier, flipping the item/phase to `IN PROGRESS` (`roadmap.py set-status <ID> "IN PROGRESS"`). A build's first change never lands on your previous branch or `HEAD`.
- Between devs, pause: after a dev's progress table (multi-phase) and its commit message, stop and wait for the user to commit before creating the next dev's branch — whether the next dev is the following phase or a separate work item. Each dev needs its own branch, cut from a clean tree.

## Definition of Done

A dev is done only when all five hold:

1. The full build succeeds with no warning the baseline did not have.
2. The entire test suite passes, bar the tests the baseline already failed, including the new tests the plan's acceptance criteria call for.
3. Every acceptance criterion in the plan file is met.
4. The roadmap and plan file statuses are updated (`roadmap.py set-status`).
5. The dev's completion doc `docs/done/<ID>.md` is written (core *Completion docs*).

Only then print the progress table (multi-phase) and the suggested commit message. **Never mark an item `DONE` — or present it as finished — with a failing build or a failing test the baseline did not have**; report the failure instead.

**Baseline.** Before the dev's first change — before you create its branch, or switch to it — run the full build and the whole suite on the `HEAD` you start from, and record the build warnings by ID and file, with their count, and the failing tests by name. Criteria 1–2 count only what is new against it: a warning beyond the baseline's count for its ID and file, a failing test it does not list. What it lists is pre-existing — a follow-up, left alone unless the plan targets it; never fix unrelated code to clear it. A clean baseline keeps the strict rule: zero warnings, every test passing. The done doc records the baseline under *Build/test evidence* and lists the pre-existing warnings and failures under *Deviations & follow-ups*.

Work with no build step or test suite (documentation, prompt or config changes) meets criteria 1 and 2 by the applicable equivalent: the artifact is well-formed and its acceptance criteria are verified by inspection or a dry run. Say explicitly that there was nothing to build or test. Criteria 3–5 still apply.

## Documentation freshness sweep (build flow)

Build flow only — the planning flow never runs it. Once a dev meets the Definition of Done, and before the progress table and commit message, check that the dev hasn't silently made user-facing docs stale.

- Scan the dev's changes for documentation they may have made stale: README files; `CLAUDE.md` and other agent-instruction files (`AGENTS.md`, …); other prose docs (`CHANGELOG.md`, `CONTRIBUTING.md`, a docs site, human-facing files under `docs/`). Exclude the workflow's own `docs/roadmap.md`, `docs/plan/` and `docs/done/` (the Definition of Done covers them), and skill/command prompt files.
- Always ask, with concrete candidates — one `AskUserQuestion` every time, even when nothing looks stale. Offer one option per file/section you recommend updating, each with a one-line reason (e.g. "README 'Usage' still shows the old flag"), plus a "none / skip" option and, per the core *Asking questions*, a final `A different doc — I'll name it` option for something the sweep missed. The 4-option cap leaves room for two candidates: group more into one option, or name the extras in the question text, rather than dropping any. When the sweep found nothing, say so and recommend skip. Never edit docs without asking.
- Accepted edits land in this dev's own commit, with the suggested commit message extended to mention them. A skip changes nothing.
- Non-blocking: a safety net, not a sixth Definition-of-Done criterion — it never holds a dev's `DONE` status.

## Multi-phase progress reporting

When a phase completes, print its item's progress table before the commit message — `roadmap.py progress <base ID>`: every phase with its status, the next one — the first neither `DONE` nor `ABANDONED` — marked `(next)` — then the commit title and description. A single-phase dev gets only the commit message. When the final phase completes, every phase shows `DONE` (or `ABANDONED`), no row is marked next, and the item's own roadmap row flips to `DONE` in the same update (`set-status` does it).

```
FEATURE-3A7F — User authentication

| Phase   | Title           | Status      |
|---------|-----------------|-------------|
| PHASE01 | Login flow      | DONE        |
| PHASE02 | OAuth providers | TODO (next) |
| PHASE03 | Two-factor auth | TODO        |

Commit title:
  feat(FEATURE-3A7F): add login flow (PHASE01)

Commit description:
  - email/password login with validation
  - session cookie issuance
  - unit tests for the auth service
```

## Sub-Agent Delegation

- For a large effort that decomposes cleanly into independent units, delegate those units to sub-agents, each spawned with its own fresh context, so each stays focused on one well-scoped part.
- Delegate only when the split is genuinely clean (minimal cross-dependencies, clear interfaces between parts). Keep tightly coupled work in a single context rather than forcing an artificial split.
- When you delegate: (1) give each sub-agent the interface contract it must honor, the relevant validated requirements from the plan, and the exact target paths; (2) sub-agents write code and tests only — all git actions, roadmap/plan/done updates and commit messages remain yours; (3) after integrating their output, run the full build and test suite yourself before declaring the dev done.
