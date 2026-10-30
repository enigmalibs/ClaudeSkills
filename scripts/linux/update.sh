#!/usr/bin/env bash
# Installs or updates this checkout's skills and commands in the user's Claude folder
# ($CLAUDE_CONFIG_DIR, else ~/.claude). Each skill folder and command file replaces the
# item of the same name there; every other skill or command is kept untouched.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: update.sh [--dry-run]

Copies this checkout's skills/ and commands/ into the Claude folder
($CLAUDE_CONFIG_DIR, else ~/.claude). Skills and commands of the same
name are replaced; every other skill or command there is kept.

  -n, --dry-run   show what would change, change nothing
  -h, --help      show this help
EOF
}

fail() {
    printf 'update.sh: %s\n' "$1" >&2
    exit 1
}

report() {
    printf '  %-8s %s\n' "$1" "$2"
}

dry_run=false
for arg in "$@"; do
    case $arg in
        -n | --dry-run) dry_run=true ;;
        -h | --help) usage; exit 0 ;;
        *) printf 'update.sh: unknown argument: %s\n\n' "$arg" >&2; usage >&2; exit 2 ;;
    esac
done

repo=$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)
[[ -d $repo/skills && -d $repo/commands ]] ||
    fail "no skills/ and commands/ in $repo - run the copy of this script inside a ClaudeSkills checkout."
target=${CLAUDE_CONFIG_DIR:-${HOME:?HOME is not set}/.claude}
[[ -e $target && ! -d $target ]] && fail "$target exists and is not a folder."

added=0 replaced=0 linked=0 kept=0

# A copy is staged beside its destination, then renamed into place: a failed copy leaves
# the installed version as it was, and the trap removes the half-written staging copy.
staging=
trap '[[ -z $staging ]] || rm -rf -- "$staging"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# install_item <source item> <target folder>
install_item() {
    local src=$1 dest_dir=$2 name=${1##*/}
    local dest=$dest_dir/$name

    if [[ -L $dest && $(readlink -f -- "$dest") == "$(readlink -f -- "$src")" ]]; then
        report linked "$name (links into this checkout, left as is)"
        linked=$((linked + 1))
        return
    fi
    if [[ -L $dest ]]; then
        report replace "$name (the link to $(readlink -- "$dest") is replaced, its target is kept)"
        replaced=$((replaced + 1))
    elif [[ -e $dest ]]; then
        report replace "$name"
        replaced=$((replaced + 1))
    else
        report add "$name"
        added=$((added + 1))
    fi
    if $dry_run; then
        return
    fi

    staging=$dest_dir/.$name.update-$$
    cp -R -- "$src" "$staging" || fail "could not copy $src - $name is unchanged."
    # A link is removed on its own (no trailing slash, no -r): what it points to is never touched.
    if [[ -L $dest || ! -d $dest ]]; then
        rm -f -- "$dest"
    else
        rm -rf -- "$dest"
    fi
    mv -- "$staging" "$dest" || fail "could not move $staging to $dest."
    staging=
}

# sync_folder <label> <source folder> <target folder> <source item>...
sync_folder() {
    local label=$1 src_dir=$2 dest_dir=$3
    shift 3
    local -A owned=()
    local item entry name

    printf '\n%s -> %s\n' "$label" "$dest_dir"
    [[ -e $dest_dir && ! -d $dest_dir ]] && fail "$dest_dir exists and is not a folder."
    if [[ -d $dest_dir && $(readlink -f -- "$dest_dir") == "$(readlink -f -- "$src_dir")" ]]; then
        report skip "this is the checkout's own $label folder - nothing to do"
        return
    fi
    if [[ ! -d $dest_dir ]]; then
        report create "$dest_dir"
        $dry_run || mkdir -p -- "$dest_dir"
    fi

    for item in "$@"; do
        owned[${item##*/}]=1
        install_item "$item" "$dest_dir"
    done

    [[ -d $dest_dir ]] || return 0
    for entry in "$dest_dir"/*; do
        name=${entry##*/}
        [[ -n ${owned[$name]:-} ]] && continue
        report keep "$name"
        kept=$((kept + 1))
    done
}

shopt -s nullglob
skills=()
for item in "$repo"/skills/*/; do
    skills+=("${item%/}")
done
commands=()
for item in "$repo"/commands/*.md; do
    [[ -f $item ]] && commands+=("$item")
done

printf 'ClaudeSkills update\n  source   %s\n  target   %s\n' "$repo" "$target"
$dry_run && printf 'Dry run - nothing is changed.\n'

sync_folder skills "$repo/skills" "$target/skills" "${skills[@]}"
sync_folder commands "$repo/commands" "$target/commands" "${commands[@]}"

if $dry_run; then
    printf '\nDry run: %d to add, %d to replace, %d linked, %d kept. Run without --dry-run to apply.\n' \
        "$added" "$replaced" "$linked" "$kept"
else
    printf '\nDone: %d added, %d replaced, %d linked, %d kept.\n' "$added" "$replaced" "$linked" "$kept"
fi
