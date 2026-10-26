---
description: Autonomous "vibe coding" run — from a spec prompt, self-answers the /interview questions with the recommended options, writes the roadmap rows + plan files, then builds every planned dev on a <feature|bugfix|review>/<date>-<slug> run branch (branch, implement, DoD, commit, merge) without asking anything. No argument = resume the run of the current run branch. Never touches the branch you started from; never pushes; never adds an attribution trailer to its commits.
argument-hint: [<spec draft text> | (nothing = resume the current run)]
disable-model-invocation: true
---

# /vibe — plan a spec and build it, unattended

**Hard rules** (the `vibe-workflow` skill holds them all):
- **Never ask, never pause** — decide with the option you would have recommended, and record it.
- **Never push; never write to the branch I started from or to the default branch.**
- **Never a 4th fix cycle; never merge or mark `DONE` a red dev** — quarantine it and continue.
- **No `Co-Authored-By` or other attribution line in any commit**, even if the session asks for one.

You plan the spec yourself, answering the interview on my behalf, then run the skill's build loop and report once, at the end. Everything not written here is the skill's.

## Phase 0: Announce the version
**Before anything else**, your very first output must be exactly this line, as plain text, on its own line and with nothing before it:

Using vibe v6 by Josué Clément

## Phase 1: Load the standards
Load the **`dev-workflow`** skill and read its `reference/build-flow.md`, then load the **`vibe-workflow`** skill — the override layer, which wins wherever they disagree; here `<command>` = `vibe`. Load the stack/convention skills the codebase calls for (as `/interview` Phase 1 step 5b).

## Phase 2: Pre-flight and mode
Run the skill's pre-flight (§10). **An argument → NEW RUN** (Phase 3), cut from the current `HEAD` whatever it is — even another run branch. **No argument → RESUME** per the skill's §9, or stop with `vibe: nothing to resume here — pass a spec to start a run.`

## Phase 3: Self-interview (new run)
Run `/interview`'s Phase 1 in spirit and answer it yourself:
1. Read the draft. A code-review input (findings with severities, usually `file:line`) → a `CODE-REVIEW-HHHH` item, findings as severity-ordered phases on `review/` branches; otherwise `FEATURE` or `BUG` by content.
2. Explore the codebase before deciding — build files, dependency manifests, DI setup, test framework, naming conventions, the modules the work touches. Never decide from assumption what the code answers.
3. Walk `dev-workflow`'s *Beyond-the-draft checklist*: each dimension covered, decided here, or not applicable with a one-line reason.
4. Generate the questions `/interview` would ask, highest impact first, and answer each with the option you would mark "(Recommended)", with its rationale.
5. Break the work down: type, title (≤ 40 characters), phases, branch names — one dev = one reviewable commit (~30 minutes of review); prefer more, smaller phases. IDs from `roadmap.py new-id`.
6. Print the summary once — objective · context · decisions table · conventions applied · beyond-the-draft table · breakdown — and continue: there is no confirmation step.

## Phase 4: Plan and commit (new run)
1. `git switch -c <category>/<yyyy-mm-dd>-<slug>` — the run branch (skill §3); an existing name is the §10 collision stop.
2. Create the `docs/` structure if missing; add the rows with `roadmap.py add` (`TODO`); write one plan file per item in the house shape — Status · Type · Branch · the `Run:` marker (§9) · objective · context & constraints · decisions · per-phase steps and acceptance criteria · out of scope — plus `## Decisions taken autonomously` (*Question · Chosen · Why · Alternatives rejected*).
3. Stage those files explicitly and commit `docs(roadmap): plan <ID>[, <ID>…]` (§4).

## Phase 5: Build, then report
Run the skill's §6 build loop until no run item has a buildable `TODO`, then stay on the run branch and print the §11 end-of-run report.

---

# My Specifications Draft:
$ARGUMENTS

*(If the draft above is empty, this is a **resume**: do not invent requirements and do not treat earlier conversation as the draft — resolve the run from the current branch per Phase 2, or stop with `vibe: nothing to resume here — pass a spec to start a run.`)*
