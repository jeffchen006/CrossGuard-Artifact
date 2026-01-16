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
  parts=( "$ZIP_DIR/$bench".z[0-9][0-9] "$ZIP_DIR/$bench".z[0-9][0-9][0-9] )
  if [ "${#parts[@]}" -gt 0 ]; then
    if command -v 7z >/dev/null 2>&1; then
      7z x -y -o"$OUT_DIR" "$zip_path" >/dev/null
    elif command -v zip >/dev/null 2>&1; then
      tmp_dir="$ZIP_DIR/.tmp"
      mkdir -p "$tmp_dir"
      tmp_zip="$(mktemp -p "$tmp_dir" "${bench}.combined.XXXXXX.zip")"
      zip -s 0 "$zip_path" --out "$tmp_zip" >/dev/null
      unzip -q "$tmp_zip" -d "$OUT_DIR"
      rm -f "$tmp_zip"
    else
      echo "Error: split zip detected for $bench but neither 7z nor zip is available." >&2
      exit 1
    fi
  else
    unzip -q "$zip_path" -d "$OUT_DIR"
  fi
done

echo "Done."
