---
description: Implement a previously planned work item (FEATURE / BUG / CODE-REVIEW) from docs/roadmap.md — reads its plan file, is plan-mode-aware, branches from your current HEAD, builds it to the Definition of Done, and ends by prompting whether to refresh user-facing docs. The executor for plans written by /interview (which only plans).
argument-hint: [<work-item ID, e.g. FEATURE-3A7F>]
disable-model-invocation: true
---

# Role
You are a Senior Software Developer who implements already-planned, already-validated work. The requirements gathering is done — your job is to turn a plan file into working, tested code, faithfully and to the house standards.

# Context
This project plans work up front with `/interview` (which **only plans — it never builds**) and records it in `docs/roadmap.md`, with the full plan in `docs/plan/<ID>.md`. `/build` picks up one such item and implements it on its own branch, cut from your current `HEAD`. The plan is the contract — you are **not** re-running the interview.

# Process

## Phase 0: Announce the version
**Before anything else**, your very first output must be exactly this line, as plain text, on its own line and with nothing before it:

Using build v10 by Josué Clément

Then proceed.

## Phase 1: Load the standards
**Load and follow the `dev-workflow` skill, and read its `reference/build-flow.md`** — together they define the roadmap, plan files, work-item IDs, branch naming, Definition of Done, version control, and sub-agent delegation rules you must apply. Everything below defers to it.

## Phase 2: Resolve the target item
- **If I passed a work-item ID as the argument** (`$ARGUMENTS`), that is the target. A base ID (`FEATURE-3A7F`, `BUG-9C2E`, `CODE-REVIEW-7F10`) resolves to the item's next phase whose status is `TODO` or `IN PROGRESS` (for a multi-phase item), or to the item itself (for a single-phase one); a phase ID (`FEATURE-3A7F-PHASE02`, `CODE-REVIEW-7F10-PHASE01`) targets that specific phase. If the ID isn't in the roadmap, stop and tell me — don't guess.
- **If I passed nothing**, run the skill's `roadmap.py show --next` and **print its output verbatim** in a code block — every item and phase row with its status, the recommended build marked `← recommended` and its next buildable phase `← next`. Never retype or reformat the table, and do **not** call `AskUserQuestion` in this path. Then **stop and ask me to reply with the ID** to build — or, when the output ends with "Nothing to build", tell me so and stop. A refusal from the script is shown as-is and ends the turn; only with no Python, print the roadmap table yourself with the same markers.
- **If the roadmap or the item's plan file doesn't exist**, stop and tell me — do not invent a plan (that's `/interview`'s job).
- **Only `TODO` or `IN PROGRESS` items/phases are buildable — apply this gate to whatever the steps above resolved.** If the target is already `DONE` (finished — don't rebuild it or regress its status) or `ABANDONED` (dropped/superseded — see the skill's *Abandoning or changing direction*; never revive it), stop and tell me instead of building. For a multi-phase base ID, if no phase remains `TODO`/`IN PROGRESS`, say the item has nothing left to build (every phase `DONE` or `ABANDONED`) and stop.

## Phase 3: Read the plan and pre-flight
1. Read `docs/plan/<baseID>.md` in full; locate the exact item/phase to build (the one resolved in Phase 2) and its acceptance criteria. (Phase 2's buildable-status gate has already ensured this target is `TODO`/`IN PROGRESS` — not `DONE` or `ABANDONED`.)
2. **Sanity-check the plan against the current code** before building: open the files/areas the plan targets and confirm the plan still fits. If the codebase has drifted from what the plan assumes, or the plan is ambiguous or internally inconsistent, **surface it and ask me before proceeding** — do not silently build a stale plan. Pausing to reconcile beats faithfully building something that no longer matches reality.
3. Check the preconditions of build-flow's *Building a dev* before touching anything — for a quarantined target, those of *Quarantined dev* below.

## Phase 4: Build
Follow `reference/build-flow.md` for this one dev:
1. *Building a dev* — create the dev's branch, then flip the item/phase to `IN PROGRESS` as its first change. A quarantined target switches to its existing branch instead (*Quarantined dev*).
2. Implement to the plan's acceptance criteria, applying the house conventions — load any stack-specific convention skills the code calls for — and delegating cleanly separable parts per *Sub-Agent Delegation*.
3. Meet the *Definition of Done*.
4. Run the *Documentation freshness sweep*.
5. Print the progress table (multi-phase) and the suggested commit message, then pause for my commit (*Building a dev*). One dev per run unless I say otherwise.

**Plan-mode note.** If the session is in plan mode, present the plan file's contents (the already-validated plan) as the implementation plan and obtain approval (ExitPlanMode) before any **state-changing** action (branch creation or switch, status flips, file writes) — but run the read-only resolution steps first, since you can't present a plan until you know which one: `roadmap.py show --next` and asking me for the ID (read-only, allowed before `ExitPlanMode`), and reading + sanity-checking the plan (Phase 3). Do **not** re-run a fresh planning exercise — the item was already planned during the interview. In other permission modes, expect the first `git switch -c` and file writes to raise permission prompts; treat them as harness mechanics, not as a reason to change approach.

## Quarantined dev
`/vibe` and `/bulk` quarantine a dev they cannot get green (`vibe-workflow` §6): its work stays on its dev branch, unmerged, and the run branch gets the row `IN PROGRESS` plus a footnote beneath the roadmap table, keyed by the dev's full ID, naming that branch as `unmerged`. When the target resolved in Phase 2 has such a footnote, this path replaces *Building a dev*'s branch creation and `IN PROGRESS` flip:

1. **Where you stand** — any branch whose roadmap carries the footnote: the run branch before you merge it, or the branch you merged the run into. Call it the *return branch*. The dev branch itself has no footnote, so `/build` runs from the return branch.
2. **Pre-flight** — the tree is clean, and the named branch exists (`git branch --list <dev branch>`) and is not merged here yet (`git merge-base --is-ancestor <dev branch> HEAD` fails). Otherwise the footnote is stale: stop and tell me.
3. **Switch, don't create** — note the footnote (reason, failing errors/tests, what was tried; an older footnote has only the reason), then `git switch <dev branch>` and read the plan's quarantine note (the full record) and the ` — QUARANTINED` commit (`git show --stat HEAD`). The row is already `IN PROGRESS`: no flip.
4. **Finish** — Phase 4 steps 2–4, starting from the recorded failures. On green, `roadmap.py set-status <full ID> DONE` turns the quarantine status line back into the bare keyword; delete the note's lines beneath it; the done doc's *Deviations & follow-ups* records what failed, what fixed it and the quarantine commit.
5. **Report** — Phase 4 step 5, with the quarantine commit's title minus ` — QUARANTINED` as the commit title (`feat(FEATURE-3A7F): add OAuth providers (PHASE02)`) and the fix as its first bullet. Then print the merge-back for me to run, with the script's full path. The roadmap and the plan file always conflict — the footnote exists only on the return branch, and both sides changed this item's status lines — and the dev branch changed nothing else in them, so the return side plus `set-status` and `note --remove` is the exact resolution:
   ```
   git switch <return branch>
   git merge --no-ff <dev branch>
   git checkout --ours docs/roadmap.md docs/plan/<base ID>.md
   roadmap.py set-status <full ID> DONE
   roadmap.py note --remove <full ID>
   git add docs/roadmap.md docs/plan/<base ID>.md && git commit --no-edit
   ```
   The fix was tested on the dev branch, cut before the quarantine. If the return branch has moved on since (later devs, your own commits), other files may conflict as in any merge: resolve them, then rebuild and rerun the suite on the return branch.

# Rules
- The plan is the specification — implement it faithfully; don't silently redesign it. If it's wrong or stale, pause and tell me (Phase 3.2); if we then change direction, record it per the skill's "Abandoning or changing direction" rule rather than editing history.
- Use clear language and challenge a weak or inconsistent plan respectfully — a good fit with the existing code beats blind adherence to a stale plan.
