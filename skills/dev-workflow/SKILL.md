---
name: dev-workflow
description: Use when planning or implementing tracked work items under this house dev workflow — the roadmap registry (docs/roadmap.md) and its roadmap.py script, per-item plan files (docs/plan/<ID>.md), completion records (docs/done/<ID>.md), FEATURE-HHHH/BUG-HHHH/CODE-REVIEW-HHHH work-item IDs, branch naming, and, in its build-flow reference, the Definition of Done and multi-phase progress reporting. Loaded by the /interview, /build, /vibe and /bulk commands; apply it whenever allocating a work-item ID, writing a plan file, branching for a dev, or reporting a dev as done.
---

# Dev workflow — house planning, tracking & version-control standards

**Version: dev-workflow v9.**

## Hard rules

- **Never commit changes yourself** — the user commits (*Version Control*).
- **A build branches from the current `HEAD`, never from the default branch** (`reference/build-flow.md`).
- **Never mark a dev `DONE` with a failing build or failing tests** (`reference/build-flow.md`).
- **Line endings are recommendation-only** — never fixed in a dev, never asked about (*Line endings*).
- **Every open question ends with the `None of these — I'll describe it` option** (*Asking questions*).
- Roadmap edits, status flips, footnotes, IDs and progress tables go through `scripts/roadmap.py` (*roadmap.md*).

How tracked work is planned, recorded and delivered: `/interview` plans, `/build` builds one planned item, `/vibe` and `/bulk` add `vibe-workflow` on top. A codebase's own conventions (docs layout, branch naming, roadmap or ID scheme) win — confirm them before allocating IDs or branching.

A *dev* is one deliverable unit of work — a single-phase item, or one phase of a multi-phase item — with its own branch, roadmap status update, completion record and suggested commit message.

## Two flows: planning vs building

- Planning flow — write the roadmap row(s) and plan file(s) at `TODO` on your current branch or `HEAD`, and create no dev branch. The plan file is the durable contract a later build consumes. `/interview` always runs this flow and never implements.
- Build flow — create the dev's branch from the current `HEAD` first, then implement. Uncommitted planning artifacts are its first change — a new row and plan written directly at `IN PROGRESS` — or, for an existing plan, flipping its item/phase to `IN PROGRESS`. `/build` runs this flow on an already-planned item; `/interview` never does.

The build flow's procedures — branching, the Definition of Done, the documentation freshness sweep, the pause between devs, progress reporting, sub-agent delegation — are in [`reference/build-flow.md`](reference/build-flow.md): read it before building a dev. The planning flow never needs it.

## Asking questions (both flows)

Ask the user for every decision like this, whatever the flow or command.

- Ask through `AskUserQuestion`, never as a prose list — even for a free value (a name, a path, a number): offer 2–3 plausible sample values plus the escape option.
- **Always leave a free-text way out:** end with an explicit option using the constant stem `None of these — I'll describe it`, with a question-specific description of what to type (e.g. "type the pattern you want, or 'defer this decision'"). Omit it only when the options provably enumerate every answer — a yes/no, or a pick-one-of-N like `FEATURE` / `BUG` / `CODE-REVIEW` — where the tool's automatic "Other" is enough. Approach, design, scope, naming, priorities and preferences are open by default: the burden of proof is on the claim that a set is closed. (This overrides `AskUserQuestion`'s advice against authoring an "Other": the automatic one is too easy to miss.)
- Budget the 4-option cap: an open question carries at most 3 concrete options plus the escape option. Group extra candidates or name them in the question text; never drop one silently.
- The escape option is always last and never carries `(Recommended)`; the recommendation is a concrete default listed first.
- A typed answer is a decision: adopt it, restate your reading in one line, and continue without a confirmation round. In an interview, record it under *"Decisions you made"* in the Phase 3 summary.

## Planning & Documentation

### Documentation structure (at the solution root)

- `docs/roadmap.md` — the single, persistent registry of every work item in the project.
- `docs/plan/` — one plan file per work item.
- `docs/done/` — one completion record per completed dev.
- Missing (a new project, or its first tracked item)? Create it — the roadmap as an empty four-column table — after confirming work items aren't tracked elsewhere.

### Work-item identifiers

- Format: `FEATURE-HHHH`, `BUG-HHHH` or `CODE-REVIEW-HHHH`, where `HHHH` is random uppercase hex — e.g. `FEATURE-3A7F`. IDs carry no order; the roadmap's row order does.
- Allocate with `roadmap.py new-id <TYPE>`: it draws securely at random, redraws on a same-type collision in the roadmap or `docs/plan/` (`ABANDONED` items included), and warns about stray plan files. Never invent the hex yourself — hand-picked values are not uniform. Random IDs let devs allocate concurrently without a shared counter. Uniqueness is per type: `FEATURE-3A7F` and `BUG-3A7F` may coexist.
- A multi-phase item suffixes each phase as `-PHASENN` (2-digit, sequential): `FEATURE-3A7F-PHASE01`, `FEATURE-3A7F-PHASE02`, …; the base keeps its un-suffixed ID. Phases never collide, since one dev owns a multi-phase item.
- A `CODE-REVIEW-HHHH` item captures a code review (`/code-review`, `/security-review`, a PR review). Each finding is one phase, ordered highest severity first (Critical → High → Medium → Low), with the severity in the phase title — `PHASE01 — [Critical] SQL injection in OrderRepository`. Its plan file records each finding's severity, location (`file:line`) and recommended fix. Built like any multi-phase item, on `review/` branches.

### `roadmap.md` — summary only

One summary table — never plan details — with the columns ID · Title · Status · Plan (the plan file's path), read raw (editor, `git diff`, console), so it stays aligned:

- Every column is padded to its widest cell, header included, counted in characters, not bytes; the delimiter row's dashes match. Cells are never truncated.
- Titles stay short (about ≤ 40 characters): one long title pads every row; the plan file holds the full statement.
- Status is the bare keyword `TODO`, `IN PROGRESS`, `DONE` or `ABANDONED`.
- Row order is the order: a new item is appended as the last row, and `/build` recommends the topmost `IN PROGRESS`, else `TODO`, item.
- A multi-phase item has its row, then one `- PHASENN` row per phase with its own status and the plan cell `(in FEATURE-3A7F.md)`. The item's status follows its phases: `IN PROGRESS` once one starts; once every phase is `DONE` or `ABANDONED`, `DONE` if at least one is `DONE`, else `ABANDONED`; otherwise unchanged. Its next phase — the one `/build` resolves and the progress table marks — is the first that is neither `DONE` nor `ABANDONED`.
- It is updated after every dev; a new item's row lands in the planning flow on the current branch, or as a build's first change on its dev branch.

```markdown
| ID           | Title               | Status      | Plan                      |
|--------------|---------------------|-------------|---------------------------|
| FEATURE-3A7F | User authentication | IN PROGRESS | docs/plan/FEATURE-3A7F.md |
| - PHASE01    | Login flow          | DONE        | (in FEATURE-3A7F.md)      |
| - PHASE02    | OAuth providers     | IN PROGRESS | (in FEATURE-3A7F.md)      |
| BUG-9C2E     | Fix token refresh   | DONE        | docs/plan/BUG-9C2E.md     |
```

`scripts/roadmap.py` (in this skill's base directory, printed when it loads; Python 3 stdlib — `python3`, or `py -3` on Windows) keeps these invariants on every edit — never pad the table by hand:

| Subcommand | Does |
|---|---|
| `add ID "Title" [--phase "Title"]… [--status "IN PROGRESS"]` | appends the item and phase rows (`TODO`; a build starts them `IN PROGRESS`) |
| `set-status ID[-PHASENN] STATUS` | flips the row and the plan's matching Status line; the base follows its phases (rule above) |
| `fmt [--check]` | re-pads the table; other text untouched |
| `new-id TYPE` · `show [--next]` · `progress ID` | an ID · the table, marking the recommended build · a phase progress table |
| `note ID[-PHASENN] 'TEXT'` · `note --remove ID[-PHASENN]` | adds — or replaces in place — the one-line footnote ``> `ID` TEXT`` beneath the table, a blank line apart from the others · removes it. Single-quote `TEXT`: it usually holds backticks, which bash and PowerShell expand inside double quotes |

It finds `docs/roadmap.md` upward from the current directory (or `--root`). A refusal writes nothing and exits 1 with the reason. With no Python, edit by hand: re-pad every row to each column's widest cell, flip the plan's Status line in the same edit, write a footnote as one ``> `ID` text`` line a blank line apart from the table and the other footnotes, and draw IDs with `openssl rand -hex 2`.

### Plan files — `docs/plan/<ID>.md`

One file per work item, named after its base ID (no phase suffix). It holds the full plan, proportional to the work: objective, scope, design, acceptance criteria and, for a multi-phase item, a section per phase with its steps and its own Status line. A phase rarely needs more than ~120 lines; link long context instead of pasting it. The roadmap's Plan column always points here.

### Beyond-the-draft checklist

Planning walks these 13 dimensions whatever the draft says, and reports how each was resolved: security & authentication/authorization · input validation & abuse cases · performance & scalability targets · concurrency · error handling & resilience (timeouts, retries, partial failures) · UX edge cases (empty/loading/error/offline states) · accessibility & internationalization · observability (logging, metrics, diagnostics) · data migration & compatibility · deployment & operations · licensing & third-party dependencies · testing · documentation. Line endings are never one of them (*Line endings*).

### Completion docs — `docs/done/<ID>.md`

One record per completed dev, named after its full ID, phase suffix included: `docs/done/FEATURE-3A7F-PHASE02.md`, `docs/done/BUG-1F3D.md`. It lands in the dev's own commit, and writing it is Definition-of-Done criterion 5. Sections:

- Summary — what changed and why.
- Files/modules touched — created / modified / deleted, as paths only; the diff carries the detail.
- Deviations & follow-ups — where the build differed from the plan and why, known issues, follow-ups, and any line-ending recommendation.
- Build/test evidence — the Definition-of-Done proof: the commands run and their pass/fail counts, the tests added, or (with no build or tests) how each criterion was verified.

Aim for about 40 lines for a single-phase dev: record what a reviewer cannot read from the diff.

### Abandoning or changing direction

Never delete a dropped item's row. Set its status to `ABANDONED` (`set-status`) and give the reason — and the replacing item's ID, if any — as a footnote beneath the table, keyed by the ID (`note`); mirror the note at the top of its plan file. (A sentence in the Status cell would widen that column for every row.) A dropped phase is abandoned the same way, keyed by its phase ID; the item's row then follows its phases (*roadmap.md*).

```
roadmap.py note FEATURE-4B21 'abandoned — superseded by a simpler approach; replaced by `FEATURE-8D0C`.'
```

```markdown
> `FEATURE-4B21` abandoned — superseded by a simpler approach; replaced by `FEATURE-8D0C`.
```

## Line endings (CRLF)

Never fix CRLF / line-ending noise in a dev, and never raise it as an interview question. If you notice it (a diff dominated by CRLF↔LF churn, mixed endings in a touched file), write a one-line recommendation — in the completion doc's *Deviations & follow-ups* and/or the console — and take no action. Normalizing (e.g. a `.gitattributes` `* text=auto eol=lf` rule) is the user's call.

## Version Control

- Never commit changes yourself — the user commits. Creating a dev branch (build flow) is the only git action you take that modifies the repository; read-only commands (`git status`, `log`, `diff`, `branch --list`, `rev-parse`) are always fine.
- Branch names: a category folder — `feature/`, `bugfix/` or `review/` — then the ID lowercased: `feature/feature-3a7f-<slug>`, `bugfix/bug-9c2e-<slug>`, `review/code-review-7f10-<slug>`. A phase is included, one branch per phase: `feature/feature-3a7f-phase01-<slug>`.
- The planning flow creates no dev branch: its rows and plan files land on the current branch or `HEAD`, and branching is left to whoever builds the item.
- After each dev, print — never run — a suggested commit message: a short title, a blank line, a brief bulleted description. Conventional-commit style with the base ID as the scope: `feat(FEATURE-3A7F): …`, `fix(BUG-9C2E): …`, `fix(CODE-REVIEW-7F10): …`. A phase goes in the title, never the scope: `feat(FEATURE-3A7F): add login flow (PHASE01)`.
- The planning flow suggests one documentation commit for the batch, scoped `docs` (or `chore`): `docs(roadmap): plan FEATURE-5C4D, FEATURE-6E1A, BUG-1F3D` — not a per-item `feat(...)` / `fix(...)`, which belongs to the build.
