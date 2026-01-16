#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

DB_DIR="$REPO_ROOT/crawlPackage/database"
DB_FILE="$DB_DIR/etherScan.db"
ZIP_DIR="$DB_DIR/etherScan_db_zips"
FORCE="${FORCE:-0}"

if [ -f "$DB_FILE" ] && [ "$FORCE" != "1" ]; then
  echo "Skip etherScan.db (already present)"
  exit 0
fi

if [ "$FORCE" = "1" ] && [ -f "$DB_FILE" ]; then
  rm -f "$DB_FILE"
fi

if [ ! -d "$ZIP_DIR" ]; then
  echo "No zip directory found at $ZIP_DIR; skipping." >&2
  exit 0
fi

zip_path="$ZIP_DIR/etherScan.db.zip"
if [ ! -f "$zip_path" ]; then
  echo "No zip archive found at $zip_path; skipping." >&2
  exit 0
fi

mkdir -p "$DB_DIR"

parts=( "$ZIP_DIR/etherScan.db".z[0-9][0-9] "$ZIP_DIR/etherScan.db".z[0-9][0-9][0-9] )
if [ "${#parts[@]}" -gt 0 ]; then
  if command -v 7z >/dev/null 2>&1; then
    7z x -y -o"$DB_DIR" "$zip_path" >/dev/null
  elif command -v zip >/dev/null 2>&1; then
    tmp_dir="$ZIP_DIR/.tmp"
    mkdir -p "$tmp_dir"
    tmp_zip="$(mktemp -p "$tmp_dir" "etherScan.db.combined.XXXXXX.zip")"
    zip -s 0 "$zip_path" --out "$tmp_zip" >/dev/null
    if ! command -v unzip >/dev/null 2>&1; then
      echo "Error: unzip not found. Install unzip and re-run." >&2
      rm -f "$tmp_zip"
      exit 1
    fi
    unzip -q "$tmp_zip" -d "$DB_DIR"
    rm -f "$tmp_zip"
  else
    echo "Error: split zip detected but neither 7z nor zip is available." >&2
    exit 1
  fi
else
  if ! command -v unzip >/dev/null 2>&1; then
    echo "Error: unzip not found. Install unzip and re-run." >&2
    exit 1
  fi
  unzip -q "$zip_path" -d "$DB_DIR"
fi

echo "Done."
