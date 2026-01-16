#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ZIP_DIR="$REPO_ROOT/constraintPackage/cache/functionAccess_zips"

REMOTE="${REMOTE:-origin}"
MAX_BYTES="${MAX_BYTES:-1932735283}"
DRY_RUN="${DRY_RUN:-0}"

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git not found." >&2
  exit 1
fi

if ! git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  echo "Error: not a git repository: $REPO_ROOT" >&2
  exit 1
fi

BRANCH="${BRANCH:-$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD)}"
if [ "$BRANCH" = "HEAD" ]; then
  echo "Error: detached HEAD; set BRANCH explicitly." >&2
  exit 1
fi

if ! git -C "$REPO_ROOT" remote get-url "$REMOTE" >/dev/null 2>&1; then
  echo "Error: remote not found: $REMOTE" >&2
  exit 1
fi

if [ -n "$(git -C "$REPO_ROOT" diff --cached --name-only)" ]; then
  echo "Error: index has staged changes. Commit or reset them first." >&2
  exit 1
fi

if [ ! -d "$ZIP_DIR" ]; then
  echo "Error: zip directory not found: $ZIP_DIR" >&2
  exit 1
fi

shopt -s nullglob
mapfile -t files < <(find "$ZIP_DIR" -type f \
  \( -name '*.zip' -o -name '*.z[0-9][0-9]' -o -name '*.z[0-9][0-9][0-9]' -o -name '*.z[0-9][0-9][0-9][0-9]' \) \
  -printf '%p\n' | sort)

if [ "${#files[@]}" -eq 0 ]; then
  echo "No zip parts found under $ZIP_DIR" >&2
  exit 0
fi

sizes=()
for f in "${files[@]}"; do
  size=$(stat -c %s "$f")
  if [ "$size" -gt "$MAX_BYTES" ]; then
    echo "Error: file larger than MAX_BYTES: $f ($size bytes)" >&2
    exit 1
  fi
  sizes+=("$size")
done

commit_batch() {
  local idx="$1"
  local size_bytes="$2"
  shift 2
  local items=("$@")
  local rels=()
  local f

  for f in "${items[@]}"; do
    rels+=("${f#$REPO_ROOT/}")
  done

  if [ "$DRY_RUN" = "1" ]; then
    echo "Batch $idx: ${#rels[@]} files, ${size_bytes} bytes"
    return
  fi

  git -C "$REPO_ROOT" add -- "${rels[@]}"
  if git -C "$REPO_ROOT" diff --cached --quiet -- "${rels[@]}"; then
    echo "Batch $idx: nothing to commit"
    return
  fi

  git -C "$REPO_ROOT" commit -m "Add functionAccess zip cache batch $idx"
  git -C "$REPO_ROOT" push "$REMOTE" "$BRANCH"
}

batch=()
batch_size=0
batch_idx=1

for i in "${!files[@]}"; do
  f="${files[$i]}"
  sz="${sizes[$i]}"
  if [ "$batch_size" -gt 0 ] && [ $((batch_size + sz)) -gt "$MAX_BYTES" ]; then
    commit_batch "$batch_idx" "$batch_size" "${batch[@]}"
    batch_idx=$((batch_idx + 1))
    batch=()
    batch_size=0
  fi
  batch+=("$f")
  batch_size=$((batch_size + sz))
done

if [ "${#batch[@]}" -gt 0 ]; then
  commit_batch "$batch_idx" "$batch_size" "${batch[@]}"
fi

