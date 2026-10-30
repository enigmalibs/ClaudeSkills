# FEATURE-C001-PHASE01 — Linux update.sh

## Summary

`scripts/linux/update.sh` installs or updates this checkout's skills and commands in `$CLAUDE_CONFIG_DIR`, or `~/.claude` when that is unset:
- **Same-named items are replaced whole:** each `skills/<name>/` folder and each `commands/*.md` file. The copy is staged beside the destination and then renamed into place, so a failed copy leaves the installed version intact.
- **Everything else is kept and listed** as `keep`.
- **Links:**
  - a link into this checkout is left as is (`linked`);
  - a link elsewhere has the link itself replaced, and its target is never touched;
  - a target `skills`/`commands` folder that *is* the checkout's own folder is skipped.
- **Missing target folders** are created on a real run.
- **`--dry-run` / `-n`** prints the same lines and changes nothing. That includes a target that is missing or empty.
- **Exit codes:** `0` done · `1` error · `2` unknown argument.

README:
- the repository tree gains `scripts/`;
- the copy-install sentence now points to the script;
- *Update and uninstall* says a copy install re-runs it after the pull.

## Files/modules touched

- Created: `scripts/linux/update.sh` (mode `100755`, LF), `docs/done/FEATURE-C001-PHASE01.md`
- Modified: `README.md`, `docs/roadmap.md`, `docs/plan/FEATURE-C001.md`

## Deviations & follow-ups

- **Baseline, not "still pass":** `html-report`'s suite was already red on the run branch before this dev: 1 failure (`test_keeps_the_template_crlf_newlines`) and 1 error (`test_changes_nothing_else_outside_the_content_region`). Both expect `templates/report.html` with CRLF, but this checkout stores it with LF. The DoD was therefore measured as "no failure beyond the baseline", per the README's *Definition of Done*. Follow-up, recommendation only: settle that template's line endings, or a `.gitattributes` rule for it, on the machine where the suite passed (34 OK).
- **Line endings:** I recommend a `.gitattributes` with `*.sh text eol=lf`, so a Windows clone with `core.autocrlf=true` can't check `update.sh` out with CRLF. Bash fails on `\r`. Not done here: normalization is the user's call.
- **Interrupts:** `INT`/`TERM` run the cleanup trap (exit 130/143). A `SIGKILL` between the copy and the rename can leave a hidden `.<name>.update-<pid>` beside the item. The next run does not list it (globs skip dot-entries), and it can be deleted by hand.

## Decisions taken at build time

| Question                        | Chosen                                                                     | Why                                                                                           |
|---------------------------------|----------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| How a foreign link is reported  | `replace  <name> (the link to <path> is replaced, its target is kept)`     | The one case where the install changes kind; saying so up front, in the dry run too           |
| Target path that is a file      | Exit 1 with `<path> exists and is not a folder.`, checked before any write | `mkdir -p` would fail halfway; a dry run would otherwise report a `create` that cannot happen |
| Which repo commands are sources | Regular `commands/*.md` files only; skills are every `skills/*/` folder    | Mirrors the README's link loops                                                               |
| Hidden entries in the target    | Not listed as `keep`                                                       | A bash glob skips them; they are neither skills Claude loads nor anything the script touches  |
| Message on a failed copy        | `could not copy <source> - <name> is unchanged.`, exit 1, the run stops    | The remaining items keep their previous version; a rerun completes the update                 |

## Build/test evidence

Nothing to compile. `bash -n` passes, the file is ASCII with LF endings and executable. All the scenarios below ran with `CLAUDE_CONFIG_DIR` set to throwaway folders in the session scratchpad, never the real `~/.claude`. The harness took 39 checks, all passing:

- **S1** — dry run, target missing: exit 0, the target is still absent, 2 `create` lines and 22 `add` lines (17 skills + 5 commands), summary `22 to add`.
- **S2** — dry run, empty `skills/` and `commands/`: exit 0, the tree hash is unchanged, no `create`, 22 `add`.
- **S3** — target copied from this machine's real install, plus foreign items: a skill folder, a namespaced `commands/frontend/`, plain files, and a stale file inside `dev-workflow`.
  - Dry run: unchanged, with every foreign item listed `keep`.
  - Real run:
    - every repo skill is `diff -r`-identical and every command `cmp`-identical to its source, with matching file modes;
    - the stale file and the old `review-standards/templates/report.html` are gone;
    - the foreign items' hashes are unchanged and no staging path is left;
    - summary `1 added, 21 replaced, 0 linked, 6 kept`.
- **S4** — links: the two links into the checkout are reported `linked` and are still links. A link to a folder elsewhere is replaced by a real copy, and the linked-to folder's hash is unchanged.
- **S5** — `skills` and `commands` are links to the checkout's own folders: both are skipped, and the checkout's hash is unchanged.
- **S6** — `--bogus` gives exit 2 with the usage on stderr. `--help` gives exit 0. A copy of the script outside a checkout, a target that is a file, and a `skills` that is a file each give exit 1.
- **S7** — a real run on a missing target installs everything. The rerun gives `0 added, 22 replaced`.
- **S8** — read-only `skills/`: exit 1 with `… avalonia is unchanged.`, the installed tree's hash is unchanged, and no staging is left.
- **Suites:**
  - `python3 -B -m unittest discover -s skills/dev-workflow/scripts`: 51 OK;
  - `… -s skills/html-report/scripts`: 34 run, the same 1 failure + 1 error as the baseline. That suite was not touched.
- **Documentation sweep:** the README tree, the install paragraph and the update section were this phase's planned edits. *Maintaining this repository* lists the Python suites only and is still accurate. There is no `CLAUDE.md`, `AGENTS.md`, `CHANGELOG.md` or `CONTRIBUTING.md`.
