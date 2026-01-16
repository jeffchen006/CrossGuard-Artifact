#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ZIP_DIR="$REPO_ROOT/constraintPackage/cache/functionAccess_zips"
OUT_DIR="$REPO_ROOT/constraintPackage/cache/functionAccess"
FORCE="${FORCE:-0}"

if ! command -v unzip >/dev/null 2>&1; then
  echo "Error: unzip not found. Install unzip and re-run." >&2
  exit 1
fi

if [ ! -d "$ZIP_DIR" ]; then
  echo "No zip directory found at $ZIP_DIR; skipping." >&2
  exit 0
fi

mkdir -p "$OUT_DIR"

shopt -s nullglob
zips=("$ZIP_DIR"/*.zip)

if [ "${#zips[@]}" -eq 0 ]; then
  echo "No zip archives found under $ZIP_DIR; skipping." >&2
  exit 0
fi

for zip_path in "${zips[@]}"; do
  bench="$(basename "$zip_path" .zip)"
  target="$OUT_DIR/$bench"
  if [ -d "$target" ] && [ "$FORCE" != "1" ] && [ -n "$(ls -A "$target" 2>/dev/null)" ]; then
    echo "Skip $bench (already present)"
    continue
  fi
  if [ "$FORCE" = "1" ] && [ -d "$target" ]; then
    rm -rf "$target"
  fi
  echo "Unpacking $bench"
  unzip -q "$zip_path" -d "$OUT_DIR"
done

echo "Done."
