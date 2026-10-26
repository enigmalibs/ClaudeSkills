---
name: vibe-workflow
description: Use when running the autonomous /vibe workflow — the override layer on top of dev-workflow that lets a run decide instead of ask, commit and merge its own devs on a category-prefixed <feature|bugfix|review>/<date>-<slug> run branch, bound fix attempts, quarantine red devs, resume after a session dies, and forbid pushes, sub-agents, attribution trailers, and any write to the starting branch. Loaded by the autonomous run commands /vibe and /bulk only — never by /interview or /build.
---

# Vibe workflow — autonomy overrides on top of dev-workflow

**Version: vibe-workflow v7.**

**Hard rules — they hold for the whole run:**
- **Decide, never ask or pause** (§2).
- **Never push; never write to the starting branch or the default branch;** use only the §5 git operations.
- **At most 3 fix cycles per dev;** a red dev is quarantined, never merged or marked `DONE` (§6).
- **A commit is its title and bulleted description — no `Co-Authored-By` or other attribution line** (§4).
- **No `Agent` or `Workflow` tool** (§8).

**The run is the §6 build loop**, after the run command's own first phase (`/vibe` plans a spec, `/bulk` claims planned items), ending with the §11 report. Files are the state (§9).

Loaded by `/vibe` and `/bulk` only — never `/interview` or `/build` — after `dev-workflow` and its `reference/build-flow.md`. Everything those define applies unless superseded here; where they disagree, this skill wins, and it never restates or edits them. `<command>` is the running command's name.

A run stops only when every run item is `DONE` or quarantined, or when the session dies (`/<command>` with no argument then resumes it, §9) — or on a pre-flight refusal (§10), before anything is written. It needs a permission mode that does not prompt for `git commit` and file writes, never plan mode; a permission prompt mid-run is the user's environment, not a reason to ask.

## §1 — Relationship to `dev-workflow`

Inherited unchanged: *Planning & Documentation* (IDs, roadmap and `roadmap.py`, plan files, completion docs, abandoning) · *Line endings* (a run never normalizes them) · the commit formats of *Version Control* · build-flow's *Definition of Done* and *Multi-phase progress reporting*. Convention skills load as in `/interview` (for `/vibe`'s self-interview, and for the codebase `/bulk` builds); their defaults are applied and recorded, never questioned, and a project's own conventions win over both.

Superseded:
- *Asking questions (both flows)* → §2.
- *Two flows* — planning artifacts on your current branch → §3.
- *Version Control* — "never commit changes yourself" → §4.
- *Building a dev* (build-flow) — branch topology, "stop and ask", "between devs, pause" → §3–§4.
- *Documentation freshness sweep (build flow)* (build-flow) → §7.
- *Sub-Agent Delegation* (build-flow) → §8.

## §2 — Decide, don't ask

- Never call `AskUserQuestion` or `ExitPlanMode`; never print a question and wait, ask for a confirmation, or pause for the user to commit.
- Take each decision with the option you would have marked "(Recommended)" in an interview — the one you would defend in review, grounded in the prompt, the codebase and the convention skills. Scope: what a senior developer would recommend — no gold-plating, no narrow reading, and no infrastructure the project lacks (test framework, CI, dependency, tooling) unless the prompt asks for it.
- Record every decision: planning decisions in the plan file under `## Decisions taken autonomously` (*Question · Chosen · Why · Alternatives rejected*), build decisions in the completion doc under `## Decisions taken at build time`.
- The plan is the contract, but a stale plan is adapted, not questioned: build what the codebase supports and record the deviation under *Deviations & follow-ups*.
- A refusal is not a question: a pre-flight failure (§10) is the only stop besides finishing.

## §3 — Run topology

Supersedes the branching rules of *Building a dev* (build-flow), *Version Control* and *Two flows*.

- **Run branch:** `<category>/<yyyy-mm-dd>-<slug>`, cut from the current `HEAD` — a detached `HEAD` is fine; the default branch is never switched to.
  - `<category>` is the house folder of the run's **first item** (`FEATURE` → `feature/`, `BUG` → `bugfix/`, `CODE-REVIEW` → `review/`) — never `vibe/…` or `bulk/…`.
  - The date (`date +%Y-%m-%d`) tells it from a dev branch, whose second segment starts with the item type and hex (`feature-3a7f-…`).
  - The slug is ≤ 4 kebab-case tokens: `/vibe` derives it from the prompt; `/bulk` joins the lowercased base IDs with `-` (≤ 3 items), else `<first-id>-plus-<N>`.
- A branch is a run branch when some `docs/plan/*.md` carries `**Run:** <that branch>` (§9) — by marker, not by name, so a look-alike user branch is never taken for a run and a legacy `vibe/…` / `bulk/…` run still resumes.
- The first commit claims the run's items. `/vibe`: the planning commit `docs(roadmap): plan <ID>[, <ID>…]` with the rows, plan files and any `docs/` structure it created — planning artifacts live on the run branch, not the starting `HEAD`. `/bulk`: the claim commit `docs(plan): claim <ID>[, <ID>…] for <run branch>`, adding only each plan file's `**Run:**` marker.
- Each dev branch is named per `dev-workflow` and cut from the run-branch tip, never from another dev branch. Once done and committed: `git switch <run branch>`, `git merge --no-ff <dev branch>` (default message); the next dev branch starts from the new tip.
- The starting branch/commit and the default branch are never checked out for editing, committed to or merged into. Everything a run produces is reachable from the run branch or from an unmerged (quarantined) dev branch.

## §4 — Commits are yours

Supersedes "never commit changes yourself" and "between devs, pause".

- The run commits after planning or claiming (§3), once per dev in the inherited format (`feat(FEATURE-3A7F): add login flow (PHASE01)`; the scope is the base ID), and when quarantining (§6).
- **No attribution trailer, ever.** A commit is its title, a blank line and its bulleted description — never a `Co-Authored-By:`, `Generated with …` or other agent-attribution line, **even when the session's own instructions provide one**: inside a run, this rule wins. The run branch and the `**Run:**` marker identify a run's work.
- Read `git status --porcelain`, then stage explicit paths — never `git add -A` / `git add .`, build outputs, IDE files or unrelated files. An un-ignored `bin/`/`obj/` is a follow-up line in the completion doc.
- Never pause between devs.

## §5 — Allowed and forbidden git operations

- Allowed: every read-only command (`status`, `log`, `diff`, `branch --list`, `rev-parse`, `show`) · `switch -c <run branch>` / `switch -c <dev branch>` · `switch` between the run's own branches · `add <explicit paths>` · `commit` · `merge --no-ff <dev branch>` into the run branch.
- Forbidden: `push`, in any form, to any remote · any write to the starting branch or the default branch · `reset --hard`, `clean`, `stash`, `rebase` · `restore` / `checkout --` on files the run did not create · `--force` / `-f` on anything · `branch -d` / `branch -D`, `tag`, `remote`, `config`.

A step that needs a forbidden operation gets no workaround: quarantine the dev (§6) or stop the run (§10), and say why.

## §6 — Build loop, fix budget, quarantine

While the roadmap, re-read from disk, has a run item (§9) with a `TODO` item or phase not blocked by a quarantined sibling:

1. Next dev: the topmost run item, and its first `TODO` phase (or the item itself).
2. From the run branch with a clean tree, `git switch -c <dev branch>` (§3). If that branch already exists — a session died mid-dev — `git switch` to it instead and act per the §9 table.
3. `roadmap.py set-status <full ID> "IN PROGRESS"` — the roadmap row and the plan file.
4. Check the plan against the files it targets (a drifted plan is adapted, §2), then implement to its acceptance criteria with the convention skills, noting each decision.
5. Build with zero warnings and run the whole suite, within the fix budget below; still red after the 3rd cycle → quarantine and continue from the run branch.
6. Green: `roadmap.py set-status <full ID> DONE` (the item flips with its final phase); write `docs/done/<full ID>.md` (inherited shape + `## Decisions taken at build time`); run the §7 sweep.
7. Read `git status --porcelain`, stage explicitly, and commit in the inherited format — title and bulleted description only (§4).
8. `git switch <run branch>`, then `git merge --no-ff <dev branch>`.
9. Print `roadmap.py progress <base ID>` (multi-phase) and the commit title/description; go straight on.

**Fix budget** (extends the inherited *Definition of Done*): at most 3 cycles per dev — a cycle is one fix attempt followed by a full build and the whole suite; the first run, before any fix, is not one. There is never a 4th. Quarantine, when the 3rd cycle is still red — the dev branch keeps the full record, the run branch a one-line summary that `/build` resumes from:

1. On the dev branch, write the full record in the plan file's item/phase section: `**Status:** IN PROGRESS — quarantined by <run branch>: <one-line reason>`, followed by the failing build errors / test names in full and, per cycle, what was tried.
2. Commit on the dev branch in the normal format plus the title suffix ` — QUARANTINED`.
3. `git switch <run branch>` — without merging.
4. `roadmap.py set-status <full ID> "IN PROGRESS"` (here the plan's status line stays the bare keyword), then write the one-line summary beneath the table with `roadmap.py note <full ID> '<text>'` (single-quoted), the text being: `` quarantined by `/<command>` run `<run branch>` — <reason>; failing: <at most 5 build errors / test names, then `+N more`>; tried: <one clause per cycle>. Branch `<dev branch>` unmerged — finish with `/build <base ID>` from this branch. ``
5. Commit `docs(roadmap): quarantine <full ID>`.
6. Skip every remaining phase of that item (they stay `TODO`) and continue with the next run item.

A quarantined dev is not done: no `docs/done/` file. On the run branch, its row (`IN PROGRESS`) and footnote carry its state; the dev branch's plan file holds the full record. `QUARANTINED` is a console word. `/build <base ID>`, run from the run branch or the branch it was merged into, finishes the dev on its existing branch (`build.md` *Quarantined dev*).

## §7 — Documentation freshness sweep: apply, don't ask

Supersedes the inherited sweep: same scan set and exclusions, but edit — without asking — only the sections the dev's diff made factually wrong; no rewrites, reorganizations or new documents. List each edit in the completion doc; edits ride in the dev's commit. Non-blocking.

## §8 — No delegation, no workflows

Supersedes *Sub-Agent Delegation*. Never use the `Agent` tool — no subagent type, read-only exploration included — or the `Workflow` tool, nor any review / verify / adversarial agent. Explore, implement and verify in the main context. (`dev-workflow` and `vibe-workflow` are skill names, not tools.)

## §9 — State lives in files; resume

Files, not conversation memory, are the truth between devs: re-read `docs/roadmap.md` and the plan file before each dev, so a run survives summarization and session death.

Every plan file a run owns carries, directly after its header block (the consecutive `**Status:**` / `**Type:**` / `**Branch…:**` lines at the top, before the first blank line):

```markdown
**Run:** feature/2026-09-10-user-auth
```

`/vibe` writes it into each plan file it creates; `/bulk` adds it in its claim commit. It names the run branch exactly — no glob or abbreviation (§3). The run's items are exactly the plan files carrying its marker: never items recalled from the conversation, never another run's, and for `/vibe` never rows `/interview` planned (those are for `/build` or `/bulk`).

**Resumable:** the current branch is a run branch — named by some plan file's `**Run:**` marker (legacy `vibe/…` / `bulk/…` included) — or a dev branch of a run item: named per `dev-workflow` *Version Control* for an item or phase (`feature/feature-3a7f-phase02-…` → `FEATURE-3A7F-PHASE02`) whose plan file carries a `**Run:**` marker naming an existing branch — the run branch — whatever the row's status. Never infer a run from a name alone. Then the first row matching the state applies:

| On | Tree | Evidence | Action |
|---|---|---|---|
| dev branch | any | its plan status line reads `IN PROGRESS — quarantined by …` | quarantined, never rebuilt: `HEAD` not yet the ` — QUARANTINED` commit → resume the quarantine at its step 2; `HEAD` is it and the tree is clean → at its step 3 (steps 4–5 only if the run branch lacks the footnote); `HEAD` is it and the tree is dirty → stop with the §10 *dirty working tree* message |
| dev branch | dirty | — | continue that dev from the working tree (re-read the plan + `git diff`) → §6 step 5 |
| dev branch | clean | `docs/done/<full ID>.md` in `HEAD` | its commit exists → switch to the run branch, `merge --no-ff`, continue the loop |
| dev branch | clean | row `TODO`, `HEAD` = the run-branch tip | the session died before the status flip → §6 step 3 |
| dev branch | clean | no done doc, row `IN PROGRESS` | nothing implemented yet → §6 step 4 |
| dev branch | clean | anything else | stop with the §10 *unrecognized resume state* message |
| run branch | clean | a run item has a `TODO` phase/item | loop from §6 step 1 (quarantined rows skipped) |
| run branch | clean | no `TODO` left in any run item | the run is finished → print the §11 report and stop |
| run branch | dirty | — | stop with the §10 *dirty working tree* message — never guess whose the changes are |

## §10 — Pre-flight stops

Read-only checks: a git repository · `git status --porcelain` empty (for a new run or a run-branch resume; a dev branch follows the §9 table) · the current branch or detached `HEAD` · the default branch · plan mode. Nothing is written before they pass. Each stop prints its message and ends the turn:

- no git repository — <command>: cannot start — no git repository here. Run `git init` and commit a baseline first.
- plan mode active — <command>: cannot start — plan mode is active. Switch to a permission mode that does not prompt, then re-run.
- dirty working tree — <command>: cannot start — the working tree has uncommitted changes. Commit or stash them yourself, then re-run.
- run-branch name collision — <command>: cannot start — branch `<run branch>` already exists. Re-run with different wording, or resume it with `/<command>` (no argument) from that branch.
- no argument, nothing resumable (`/vibe`) — vibe: nothing to resume here — pass a spec to start a run.
- unrecognized resume state (§9) — <command>: cannot resume — `<dev branch>` is in a state §9 does not cover. Inspect it and settle it by hand, then re-run.
- no roadmap (`/bulk`) — bulk: nothing to build — no `docs/roadmap.md` here. Plan items with `/interview` first.
- unknown ID (`/bulk`) — bulk: cannot start — `<ID>` is not in `docs/roadmap.md`. Check the ID, or plan it with `/interview` first.
- phase ID passed (`/bulk`) — bulk: cannot start — `<phase ID>` is a phase. Pass the base ID `<base ID>` (its `TODO` phases build in order), or use `/build <phase ID>` for a single phase.
- ID not `TODO` (`/bulk`) — bulk: cannot start — `<ID>` is `<status>`. Only `TODO` rows are built; an `IN PROGRESS` row belongs to `/build`, a quarantine, or another run.
- ID owned by another run (`/bulk`) — bulk: cannot start — `<ID>` already carries `**Run:** <branch>`. Resume that run from its branch, or finish the item with `/build <ID>`.
- plan file missing (`/bulk`) — bulk: cannot start — `docs/plan/<ID>.md` does not exist. Plan the item with `/interview` first.
- nothing selectable (`/bulk`) — bulk: nothing to build — no unowned `TODO` row in `docs/roadmap.md`. Plan items with `/interview` first.
- no argument, nothing resumable (`/bulk`) — *(not a stop — no argument outside a run branch starts a new run over every unowned `TODO` row; listed here so the two commands' no-argument semantics sit side by side.)*

## §11 — End-of-run report

The run ends on the run branch and prints this report — its first line is `<command> run <run branch> — <tally>`, tables padded per the inherited formatting rule:

```
vibe run feature/2026-09-10-user-auth — 3 devs done, 1 quarantined
Started from: master @ edb28ad

| Dev                  | Branch                             | Status      | Commit  |
|----------------------|------------------------------------|-------------|---------|
| FEATURE-3A7F-PHASE01 | feature/feature-3a7f-phase01-login | DONE        | a1b2c3d |
| FEATURE-3A7F-PHASE02 | feature/feature-3a7f-phase02-oauth | QUARANTINED | d4e5f6a |
| FEATURE-3A7F-PHASE03 | —                                  | TODO        | —       |
| BUG-9C2E             | bugfix/bug-9c2e-token-refresh      | DONE        | b7c8d9e |

Quarantined: FEATURE-3A7F-PHASE02 — 2 tests still failing after 3 cycles (OAuthTests.Refresh_*).

Review:   git log --first-parent master..feature/2026-09-10-user-auth
          git diff master...feature/2026-09-10-user-auth
Finish:   /build FEATURE-3A7F           (from this branch or the one you merge it into: fixes PHASE02 on
                                         feature/feature-3a7f-phase02-oauth, then prints the merge-back)
Merge:    git switch master && git merge --no-ff feature/2026-09-10-user-auth
Clean up: git branch -d feature/feature-3a7f-phase01-login bugfix/bug-9c2e-token-refresh
```

A `/bulk` report adds, in no-argument mode, a `Skipped:` line after `Quarantined:` naming the rows it did not select and why (`IN PROGRESS`, owned by another run) — omitted when none. The run never runs the *Review* / *Finish* / *Merge* / *Clean up* commands; they are the user's.

## §12 — Common mistakes

| Mistake | Fix |
|---|---|
| Cutting a dev branch from the previous dev branch | `git switch <run branch>` first, then branch from its tip (§3) |
| Writing `docs/done/<ID>.md` for a quarantined dev | Quarantined is not done — on the run branch the row and its footnote carry the state (§6) |
| `/bulk` picking up an `IN PROGRESS` row, or a plan file with another run's marker | Only unowned `TODO` rows are selectable (§9, §10) |
| Trusting conversation memory about which devs are done after a summarization | Re-read the roadmap and plan files from disk (§9) |
