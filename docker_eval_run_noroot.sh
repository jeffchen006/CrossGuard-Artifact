#!/usr/bin/env bash
set -euo pipefail

# A drop-in alternative to docker_eval_run.sh for systems where containers running
# as root cannot write to bind mounts (e.g., NFS root-squash, shared HPC mounts,
# some rootless Docker setups).
#
# Key difference: every `docker run` uses `--user <uid>:<gid>` and a writable HOME.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$(mktemp -t crossguard_docker_eval_noroot.XXXXXX.log)"
IMAGE_NAME="${IMAGE_NAME:-crossguard-artifact}"

# Allow overrides if needed.
DOCKER_USER="${DOCKER_USER:-$(id -u):$(id -g)}"
DOCKER_HOME="${DOCKER_HOME:-/tmp}"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "Log file: $LOG_FILE"
echo "Working dir: $SCRIPT_DIR"
echo "Image name: $IMAGE_NAME"
echo "Docker user: $DOCKER_USER"
echo "Docker HOME: $DOCKER_HOME"
echo "Start time: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo

FORGE_STD_TEST="$SCRIPT_DIR/CrossGuard_foundry/lib/forge-std/src/Test.sol"
if [ ! -f "$FORGE_STD_TEST" ]; then
  echo "==> Prep: ensure forge-std is available"
  if ! command -v git >/dev/null 2>&1; then
    echo "Error: git not found; cannot fetch forge-std."
    exit 1
  fi
  if [ -d "$SCRIPT_DIR/.git" ] \
    && [ -f "$SCRIPT_DIR/.gitmodules" ] \
    && git -C "$SCRIPT_DIR" config -f .gitmodules --get submodule.CrossGuard_foundry/lib/forge-std.url >/dev/null; then
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

docker_run_noroot() {
  # Wrapper to ensure a writable HOME and host UID/GID inside the container.
  docker run --rm \
    --user "$DOCKER_USER" \
    -e HOME="$DOCKER_HOME" \
    -v "$SCRIPT_DIR:/app" \
    -w /app \
    "$@"
}

echo "==> Step 1/6: docker build"
docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
echo

echo "==> Step 2/6: unpack functionAccess cache (if needed)"
docker_run_noroot \
  "$IMAGE_NAME" \
  bash -lc "scripts/unpack_functionAccess_zips.sh"
echo

echo "==> Step 3/6: unpack receipts DB (if needed)"
docker_run_noroot \
  "$IMAGE_NAME" \
  bash -lc "scripts/unpack_etherScan_db_zips.sh"
echo

echo "==> Step 4/6: spherex_reproduce/compute_gas_overhead.py"
docker_run_noroot \
  "$IMAGE_NAME" \
  python3 spherex_reproduce/compute_gas_overhead.py
echo

echo "==> Step 5/6: CrossGuard_foundry/gas_experiment.py"
if ! docker_run_noroot \
  "$IMAGE_NAME" \
  python3 CrossGuard_foundry/gas_experiment.py; then
  echo "Warning: gas_experiment reported mismatches; continuing."
fi
echo

echo "==> Step 6/6: runFullExperiments.py + artifact_evaluation/table_printers.py"
docker_run_noroot \
  "$IMAGE_NAME" \
  bash -lc "python3 runFullExperiments.py && python3 artifact_evaluation/table_printers.py"
echo

echo "Done."
echo "End time: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Log file: $LOG_FILE"
