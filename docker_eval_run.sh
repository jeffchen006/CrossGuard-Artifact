#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$(mktemp -t crossguard_docker_eval.XXXXXX.log)"
IMAGE_NAME="${IMAGE_NAME:-crossguard-artifact}"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "Log file: $LOG_FILE"
echo "Working dir: $SCRIPT_DIR"
echo "Image name: $IMAGE_NAME"
echo "Start time: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo

FORGE_STD_TEST="$SCRIPT_DIR/CrossGuard_foundry/lib/forge-std/src/Test.sol"
if [ ! -f "$FORGE_STD_TEST" ]; then
  echo "==> Prep: ensure forge-std is available"
  if ! command -v git >/dev/null 2>&1; then
    echo "Error: git not found; cannot fetch forge-std."
    exit 1
  fi
  if [ -d "$SCRIPT_DIR/.git" ]; then
    git -C "$SCRIPT_DIR" submodule update --init --recursive CrossGuard_foundry/lib/forge-std
  else
    FORGE_STD_DIR="$SCRIPT_DIR/CrossGuard_foundry/lib/forge-std"
    if [ -d "$FORGE_STD_DIR" ] && [ -z "$(ls -A "$FORGE_STD_DIR")" ]; then
      rmdir "$FORGE_STD_DIR"
    fi
    if [ ! -d "$FORGE_STD_DIR" ]; then
      git clone --depth 1 https://github.com/foundry-rs/forge-std "$FORGE_STD_DIR"
    else
      echo "Error: $FORGE_STD_DIR exists but forge-std is missing. Please remove it and re-run."
      exit 1
    fi
  fi
  echo
fi

echo "==> Step 1/4: docker build"
docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
echo

echo "==> Step 2/4: spherex_reproduce/compute_gas_overhead.py"
docker run --rm \
  -v "$SCRIPT_DIR:/app" \
  -w /app \
  "$IMAGE_NAME" \
  python3 spherex_reproduce/compute_gas_overhead.py
echo

echo "==> Step 3/4: CrossGuard_foundry/gas_experiment.py"
docker run --rm \
  -v "$SCRIPT_DIR:/app" \
  -w /app \
  "$IMAGE_NAME" \
  python3 CrossGuard_foundry/gas_experiment.py
echo

echo "==> Step 4/4: runFullExperiments.py + artifact_evaluation/table_printers.py"
docker run --rm \
  -v "$SCRIPT_DIR:/app" \
  -w /app \
  "$IMAGE_NAME" \
  bash -lc "python3 runFullExperiments.py && python3 artifact_evaluation/table_printers.py"
echo

echo "Done."
echo "End time: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Log file: $LOG_FILE"
