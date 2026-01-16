#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SRC_DIR="$REPO_ROOT/constraintPackage/cache/functionAccess"
ZIP_DIR="$REPO_ROOT/constraintPackage/cache/functionAccess_zips"
SPLIT_SIZE="${SPLIT_SIZE:-95m}"
FORCE="${FORCE:-0}"

if ! command -v zip >/dev/null 2>&1; then
  echo "Error: zip not found. Install zip and re-run." >&2
  exit 1
fi

if [ ! -d "$SRC_DIR" ]; then
  echo "Error: source cache not found: $SRC_DIR" >&2
  exit 1
fi

mkdir -p "$ZIP_DIR"

shopt -s nullglob
mapfile -t benchmarks < <(find "$SRC_DIR" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort)

if [ "${#benchmarks[@]}" -eq 0 ]; then
  echo "No benchmark folders under $SRC_DIR" >&2
  exit 0
fi

pushd "$SRC_DIR" >/dev/null
for bench in "${benchmarks[@]}"; do
  out="$ZIP_DIR/$bench.zip"
  if [ -f "$out" ] && [ "$FORCE" != "1" ]; then
    echo "Skip $bench (zip exists)"
    continue
  fi
  if [ "$FORCE" = "1" ]; then
    rm -f "$ZIP_DIR/$bench".z* "$out"
  fi
  echo "Zipping $bench -> $out (split $SPLIT_SIZE)"
  zip -q -r -s "$SPLIT_SIZE" "$out" "$bench"
done
popd >/dev/null

echo "Done."
