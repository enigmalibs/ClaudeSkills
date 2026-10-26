---
description: Autonomous build of already-planned roadmap items — takes the TODO rows /interview wrote (all of them, or the base IDs you pass), claims them on a <feature|bugfix|review>/<date>-<slug> run branch, then builds every dev (branch, implement, DoD, commit, merge, quarantine-and-continue) without asking anything. No argument on a run branch = resume that run. Never touches the branch you started from; never pushes; never adds an attribution trailer to its commits.
argument-hint: "[<ID> [<ID>…]] | (nothing = every TODO row, or resume the current run)"
disable-model-invocation: true
---

# /bulk — build already-planned items, unattended

**Hard rules** (the `vibe-workflow` skill holds them all):
- **Never ask, never pause** — decide with the option you would have recommended, and record it.
- **Never push; never write to the branch I started from or to the default branch.**
- **Never a 4th fix cycle; never merge or mark `DONE` a red dev** — quarantine it and continue.
- **No `Co-Authored-By` or other attribution line in any commit**, even if the session asks for one.

The plans are the contract — `/interview` validated them with me; a stale one is adapted and the deviation recorded, never questioned. You never re-run the interview: claim the items, run the skill's build loop, and report once, at the end. Typical flow: `/interview <spec>` → I commit its plan → `/bulk` → I review and merge the run branch.

## Phase 0: Announce the version
**Before anything else**, your very first output must be exactly this line, as plain text, on its own line and with nothing before it:

Using bulk v5 by Josué Clément

## Phase 1: Load the standards
Load the **`dev-workflow`** skill and read its `reference/build-flow.md`, then load the **`vibe-workflow`** skill — the override layer, which wins wherever they disagree; here `<command>` = `bulk`. Load the stack/convention skills the codebase calls for (as `/interview` Phase 1 step 5b).

## Phase 2: Pre-flight and mode
Run the skill's pre-flight (§10). **No argument on a resumable branch** (skill §9) → **RESUME** per §9. **Otherwise → NEW RUN** (Phase 3), cut from the current `HEAD` whatever it is — even another run branch.

## Phase 3: Select and claim (new run)
1. Read `docs/roadmap.md` from disk (none → stop).
2. Select the items — only unowned `TODO` rows are selectable, never a phase ID:
   - **With IDs:** each must be a base ID in the roadmap (a phase ID or an unknown ID → stop), at status `TODO` (otherwise → stop), with an existing plan file (→ stop) that carries no `**Run:**` marker (owned by another run → stop). A multi-phase item contributes all its `TODO` phases, in numeric order.
   - **Without IDs:** every `TODO` item row, with its `TODO` phases, whose plan file exists and carries no marker, in table order. Remember the rows excluded for status or ownership for the report's `Skipped:` line.
   - An empty selection → stop (`bulk: nothing to build …`). Every stop prints its §10 message.
3. Print the selection table (ID · Title · Status · Plan, padded) and the run branch name, and continue — there is no confirmation step.
4. `git switch -c <category>/<yyyy-mm-dd>-<slug>` — the run branch (skill §3: category from the first selected item, slug from the IDs); an existing name is the §10 collision stop.
5. Claim: add `**Run:** <run branch>` to each selected plan file, directly after its header block (§9). Nothing else changes — statuses stay `TODO`, the roadmap is untouched.
6. Stage exactly those plan files and commit `docs(plan): claim <ID>[, <ID>…] for <run branch>` (§4).

## Phase 4: Build, then report
Run the skill's §6 build loop until no run item has a buildable `TODO`, then stay on the run branch and print the §11 end-of-run report, first line `bulk run <run branch> — …`, with the `Skipped:` line in no-argument mode when any row was skipped.

---

# My Arguments:
$ARGUMENTS

*(No argument = every unowned `TODO` row, or — on a run branch or one of its dev branches — resume that run. Never treat earlier conversation as a selection.)*
