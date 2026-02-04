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
DOCKER_RUN_EXTRA_ARGS="${DOCKER_RUN_EXTRA_ARGS:-}"
DOCKER_ROOTLESS="unknown"
if command -v docker >/dev/null 2>&1; then
  DOCKER_ROOTLESS="$(docker info --format '{{.Rootless}}' 2>/dev/null || true)"
  if [ -z "$DOCKER_ROOTLESS" ] || [ "$DOCKER_ROOTLESS" = "unknown" ]; then
    if docker info 2>/dev/null | grep -qi '^rootless: *true'; then
      DOCKER_ROOTLESS="true"
    elif docker info 2>/dev/null | grep -qi '^rootless: *false'; then
      DOCKER_ROOTLESS="false"
    else
      DOCKER_ROOTLESS="unknown"
    fi
  fi
fi
if [ -z "${DOCKER_USER:-}" ]; then
  if [ "$DOCKER_ROOTLESS" = "true" ]; then
    # In rootless Docker, container root maps to the host user, so allow writes.
    DOCKER_USER="0:0"
  else
    DOCKER_USER="$(id -u):$(id -g)"
  fi
fi
DOCKER_HOME="${DOCKER_HOME:-/tmp}"
DOCKER_WRITABLE_ROOT="${DOCKER_WRITABLE_ROOT:-/tmp/crossguard_writable_${USER:-$(id -u)}}"
DOCKER_FORCE_WRITABLE_BINDS="${DOCKER_FORCE_WRITABLE_BINDS:-0}"
DOCKER_PROBE_WRITES="${DOCKER_PROBE_WRITES:-1}"
DOCKER_MOUNT_OPTS_RAW="${DOCKER_MOUNT_OPTS:-}"
DOCKER_MOUNT_OPTS_RAW="${DOCKER_MOUNT_OPTS_RAW#:}"
SELINUX_STATUS="unknown"
if command -v getenforce >/dev/null 2>&1; then
  SELINUX_STATUS="$(getenforce 2>/dev/null || echo unknown)"
fi
if [ -z "$DOCKER_MOUNT_OPTS_RAW" ] && [ "$SELINUX_STATUS" = "Enforcing" ]; then
  DOCKER_MOUNT_OPTS_RAW="Z"
fi
RW_MOUNT_SUFFIX=""
if [ -n "$DOCKER_MOUNT_OPTS_RAW" ]; then
  RW_MOUNT_SUFFIX=":${DOCKER_MOUNT_OPTS_RAW}"
fi
RO_MOUNT_SUFFIX=":ro"
if [ -n "$DOCKER_MOUNT_OPTS_RAW" ]; then
  RO_MOUNT_SUFFIX=":ro,${DOCKER_MOUNT_OPTS_RAW}"
fi

exec > >(tee -a "$LOG_FILE") 2>&1

echo "Log file: $LOG_FILE"
echo "Working dir: $SCRIPT_DIR"
echo "Image name: $IMAGE_NAME"
echo "Docker user: $DOCKER_USER"
echo "Docker rootless: $DOCKER_ROOTLESS"
echo "SELinux: $SELINUX_STATUS"
echo "Docker HOME: $DOCKER_HOME"
echo "Docker mount opts: ${DOCKER_MOUNT_OPTS_RAW:-<none>}"
echo "Docker extra args: ${DOCKER_RUN_EXTRA_ARGS:-<none>}"
echo "Docker writable root: $DOCKER_WRITABLE_ROOT"
echo "Docker force writable binds: $DOCKER_FORCE_WRITABLE_BINDS"
echo "Docker probe writes: $DOCKER_PROBE_WRITES"
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

can_write_dir() {
  local dir="$1"
  if [ ! -d "$dir" ]; then
    mkdir -p "$dir" 2>/dev/null || return 1
  fi
  local test_file="$dir/.codex_write_test.$$"
  if ( : > "$test_file" ) 2>/dev/null; then
    rm -f "$test_file"
    return 0
  fi
  return 1
}

configure_writable_binds() {
  DOCKER_EXTRA_MOUNTS=()

  USE_WRITABLE_CACHE="$DOCKER_FORCE_WRITABLE_BINDS"
  if [ "$USE_WRITABLE_CACHE" = "0" ]; then
    if ! can_write_dir "$SCRIPT_DIR/constraintPackage/cache/functionAccess"; then
      USE_WRITABLE_CACHE="1"
    fi
  fi
  if [ "$USE_WRITABLE_CACHE" = "1" ]; then
    CACHE_HOST="$DOCKER_WRITABLE_ROOT/constraintPackage/cache"
    mkdir -p "$CACHE_HOST/functionAccess" "$CACHE_HOST/functionAccess_zips"
    DOCKER_EXTRA_MOUNTS+=( -v "$CACHE_HOST:/app/constraintPackage/cache${RW_MOUNT_SUFFIX}" )
    DOCKER_EXTRA_MOUNTS+=( -v "$SCRIPT_DIR/constraintPackage/cache/functionAccess_zips:/app/constraintPackage/cache/functionAccess_zips${RO_MOUNT_SUFFIX}" )
    echo "Using writable cache dir: $CACHE_HOST"
  fi

  USE_WRITABLE_DB="$DOCKER_FORCE_WRITABLE_BINDS"
  if [ "$USE_WRITABLE_DB" = "0" ]; then
    if ! can_write_dir "$SCRIPT_DIR/crawlPackage/database"; then
      USE_WRITABLE_DB="1"
    fi
  fi
  if [ "$USE_WRITABLE_DB" = "1" ]; then
    DB_HOST="$DOCKER_WRITABLE_ROOT/crawlPackage/database"
    mkdir -p "$DB_HOST/etherScan_db_zips"
    DOCKER_EXTRA_MOUNTS+=( -v "$DB_HOST:/app/crawlPackage/database${RW_MOUNT_SUFFIX}" )
    DOCKER_EXTRA_MOUNTS+=( -v "$SCRIPT_DIR/crawlPackage/database/etherScan_db_zips:/app/crawlPackage/database/etherScan_db_zips${RO_MOUNT_SUFFIX}" )
    echo "Using writable DB dir: $DB_HOST"
  fi

  USE_WRITABLE_ARTIFACT="$DOCKER_FORCE_WRITABLE_BINDS"
  if [ "$USE_WRITABLE_ARTIFACT" = "0" ]; then
    if ! can_write_dir "$SCRIPT_DIR/artifact_evaluation/logs"; then
      USE_WRITABLE_ARTIFACT="1"
    fi
  fi
  if [ "$USE_WRITABLE_ARTIFACT" = "1" ]; then
    ARTIFACT_HOST="$DOCKER_WRITABLE_ROOT/artifact_evaluation"
    mkdir -p "$ARTIFACT_HOST"
    cp -a "$SCRIPT_DIR/artifact_evaluation/." "$ARTIFACT_HOST/" 2>/dev/null || true
    mkdir -p "$ARTIFACT_HOST/logs"
    DOCKER_EXTRA_MOUNTS+=( -v "$ARTIFACT_HOST:/app/artifact_evaluation${RW_MOUNT_SUFFIX}" )
    echo "Using writable artifact dir: $ARTIFACT_HOST"
  fi

  USE_WRITABLE_FOUNDRY="$DOCKER_FORCE_WRITABLE_BINDS"
  if [ "$USE_WRITABLE_FOUNDRY" = "0" ]; then
    for d in out cache broadcast; do
      if ! can_write_dir "$SCRIPT_DIR/CrossGuard_foundry/$d"; then
        USE_WRITABLE_FOUNDRY="1"
        break
      fi
    done
  fi
  if [ "$USE_WRITABLE_FOUNDRY" = "1" ]; then
    FOUNDRY_HOST="$DOCKER_WRITABLE_ROOT/CrossGuard_foundry"
    mkdir -p "$FOUNDRY_HOST"
    cp -a "$SCRIPT_DIR/CrossGuard_foundry/." "$FOUNDRY_HOST/" 2>/dev/null || true
    mkdir -p "$FOUNDRY_HOST/out" "$FOUNDRY_HOST/cache" "$FOUNDRY_HOST/broadcast"
    DOCKER_EXTRA_MOUNTS+=( -v "$FOUNDRY_HOST:/app/CrossGuard_foundry${RW_MOUNT_SUFFIX}" )
    echo "Using writable CrossGuard_foundry dir: $FOUNDRY_HOST"
  fi
}

probe_container_write() {
  local probe_user="$1"
  docker run --rm \
    --user "$probe_user" \
    -e HOME="$DOCKER_HOME" \
    -v "$SCRIPT_DIR:/app${RW_MOUNT_SUFFIX}" \
    "${DOCKER_EXTRA_MOUNTS[@]}" \
    -w /app \
    $DOCKER_RUN_EXTRA_ARGS \
    "$IMAGE_NAME" \
    bash -lc 'set -e; for d in constraintPackage/cache crawlPackage/database artifact_evaluation/logs CrossGuard_foundry/out; do mkdir -p "$d"; : > "$d/.codex_write_test"; rm -f "$d/.codex_write_test"; done'
}

docker_run_noroot() {
  # Wrapper to ensure a writable HOME and host UID/GID inside the container.
  docker run --rm \
    --user "$DOCKER_USER" \
    -e HOME="$DOCKER_HOME" \
    -v "$SCRIPT_DIR:/app${RW_MOUNT_SUFFIX}" \
    "${DOCKER_EXTRA_MOUNTS[@]}" \
    -w /app \
    $DOCKER_RUN_EXTRA_ARGS \
    "$@"
}

echo "==> Step 1/6: docker build"
docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
echo

configure_writable_binds
echo

if [ "$DOCKER_PROBE_WRITES" != "0" ]; then
  echo "==> Probe: container write access to bind mounts"
  if ! probe_container_write "$DOCKER_USER"; then
    if [ "$DOCKER_USER" != "0:0" ]; then
      echo "Probe failed with user $DOCKER_USER; trying 0:0."
      if probe_container_write "0:0"; then
        DOCKER_USER="0:0"
        echo "Using container user 0:0 for subsequent runs."
        echo
        # keep current mounts
      fi
    fi
  fi
  if ! probe_container_write "$DOCKER_USER"; then
    if [ "$DOCKER_FORCE_WRITABLE_BINDS" = "0" ]; then
      echo "Warning: container cannot write to bind mounts; enabling writable overrides."
      DOCKER_FORCE_WRITABLE_BINDS="1"
      configure_writable_binds
      echo
    fi
  fi
  if ! probe_container_write "$DOCKER_USER"; then
    echo "Error: container still cannot write to bind mounts. Try DOCKER_USER=0:0 and DOCKER_FORCE_WRITABLE_BINDS=1."
    exit 1
  fi
  echo
fi

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
