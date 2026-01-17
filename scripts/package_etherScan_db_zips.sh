#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

DB_DIR="$REPO_ROOT/crawlPackage/database"
DB_FILE="$DB_DIR/etherScan.db"
ZIP_DIR="$DB_DIR/etherScan_db_zips"
SPLIT_SIZE="${SPLIT_SIZE:-95m}"
FORCE="${FORCE:-0}"

if ! command -v zip >/dev/null 2>&1; then
  echo "Error: zip not found. Install zip and re-run." >&2
  exit 1
fi

if [ ! -f "$DB_FILE" ]; then
  echo "Error: receipts DB not found: $DB_FILE" >&2
  exit 1
fi

mkdir -p "$ZIP_DIR"

out="$ZIP_DIR/etherScan.db.zip"
if [ -f "$out" ] && [ "$FORCE" != "1" ]; then
  echo "Skip etherScan.db (zip exists)"
  exit 0
fi

if [ "$FORCE" = "1" ]; then
  rm -f "$ZIP_DIR/etherScan.db".z* "$out"
fi

pushd "$DB_DIR" >/dev/null
echo "Zipping etherScan.db -> $out (split $SPLIT_SIZE)"
zip -q -s "$SPLIT_SIZE" "$out" "etherScan.db"
popd >/dev/null

echo "Done."
