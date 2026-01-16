# CrossGuard: Artifact For the Paper "Enforcing Control Flow Integrity on DeFi Smart Contracts"

## Purpose
This artifact packages the code, datasets, and scripts used to reproduce the paper's experimental tables and key statistics for CrossGuard. 

## Badges Requested
- Available: Author-created artifacts relevant to this paper have been placed on a publicly accessible archival repository. A DOI or link to this repository along with a unique identifier for the object is provided. (10.5281/zenodo.18262998)

- Functional: The artifacts associated with the research are found to be documented, consistent, complete, exercisable, and include appropriate evidence of verification and validation.

- Reusable: The artifacts associated with the paper are of a quality that significantly exceeds minimal functionality. 


## Provenance
- Artifact location: this repository (https://github.com/jeffchen006/CrossGuard-Artifact), archived at https://zenodo.org/records/18262998

- Paper preprint: A new version has been uploaded to arxiv: https://arxiv.org/pdf/2504.05509



## Data
This artifact includes a nontrivial dataset of cached traces and transaction receipts used for the benchmarks.
- Data locations:
  - `Benchmarks_Traces/`: decoded traces and lists used by the experiments.
  - `crawlPackage/database/etherScan.db`: cached receipts and contract metadata.
  - `constraintPackage/`: large cached analysis state and derived artifacts.
  - `parserPackage/cache/` and `parserPackage/cache/*_decoded/`: decoded trace caches.
- functionAccess cache packaging:
  - Raw cache `constraintPackage/cache/functionAccess/` is stored as split zip archives under `constraintPackage/cache/functionAccess_zips/` to stay within GitHub size limits.
  - Unpack with `scripts/unpack_functionAccess_zips.sh` before running experiments (`docker_eval_run.sh` does this automatically).
- Data provenance:
  - Ethereum transaction traces and receipts, obtained from RPC endpoints and Etherscan APIs (see `settings.toml`).
  - Benchmark metadata under `benchmarkPackage/benchmarks/*.json`.
- Ethical/legal considerations:
  - All data are public blockchain traces and contract metadata. Ensure API keys are used in compliance with provider terms.
- Storage requirements (current repository sizes):
  - Total repository: ~77G.
  - Largest components: `constraintPackage/` (~73G), `crawlPackage/` (~2.5G), `Benchmarks_Traces/` (~600M).

It provides: (1) a full experiment pipeline (`runFullExperiments.py`) that produces per-benchmark logs, (2) scripts to compute SphereX overhead, and (3) a Foundry-based gas experiment to validate instrumentation overhead.

## Setup (Executable Artifact)
### Hardware
- CPU: multi-core recommended; parallel tasks run concurrently.
- Disk: at least 80 GB free for this repository.

### Software

Docker
- Docker Engine 24+ (tested with Docker 28).
- Installation: https://docs.docker.com/engine/install/
- Ubuntu quickstart (adjust for your distro):
  - `sudo apt-get update`
  - `sudo apt-get install -y ca-certificates curl gnupg`
  - `sudo install -m 0755 -d /etc/apt/keyrings`
  - `curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg`
  - `echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null`
  - `sudo apt-get update`
  - `sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin`
  - `sudo usermod -aG docker $USER` (log out/in to use Docker without sudo)
- Build in repo root using `Dockerfile`.



### What the Docker image contains
The root `Dockerfile` builds a single image that includes:
- Ubuntu 22.04 (builder stage) + Python 3.10-slim (runtime).
- Foundry binaries built from commit `fdf5732d08ce1c67aa0aaf047c3fb86614caf5ae`.
- Python dependencies used by the analysis pipeline (`tqdm`, `plotly`, `ujson`, `toml`, `requests`, `web3`, `hexbytes`, `eth-abi`, `slither-analyzer`, `packaging`, `matplotlib`).
- `solc-select` with Solidity versions `0.8.17` and `0.8.26` (default `0.8.17`).
- `vyper-select` with Vyper versions `0.3.7` and `0.2.16` (default `0.3.7`).

### Required configuration and data checks
Before running experiments, confirm:
- Cached traces and receipts exist:
  - `Benchmarks_Traces/`
  - `crawlPackage/database/etherScan.db`
  - `parserPackage/cache/` and `parserPackage/cache/*_decoded/`
- functionAccess cache is present (or unpack from `constraintPackage/cache/functionAccess_zips/`).
- `forge-std` is present for the Foundry experiment:
  - `CrossGuard_foundry/lib/forge-std/src/Test.sol` must exist.
- `settings.toml` has valid RPC endpoints and API keys (see `[settings]` in `settings.toml`).

You can quickly check:
```bash
test -f CrossGuard_foundry/lib/forge-std/src/Test.sol && echo "forge-std ok"
test -f crawlPackage/database/etherScan.db && echo "receipt DB ok"
test -d Benchmarks_Traces && echo "traces ok"
test -d constraintPackage/cache/functionAccess && echo "functionAccess ok"
```


## Usage (Reproduce Paper Results)
All commands below are run from repo root.

### One-shot Docker evaluation
Use the helper script to build the image and run all experiments in order:
```bash
./docker_eval_run.sh
```
What it does:
- Builds the Docker image.
- Unpacks `constraintPackage/cache/functionAccess_zips/` into `constraintPackage/cache/functionAccess/` if needed.
- Runs `spherex_reproduce/compute_gas_overhead.py`.
- Runs `CrossGuard_foundry/gas_experiment.py`.
- Runs `runFullExperiments.py` and then `artifact_evaluation/table_printers.py`.

Output:
- A full log is written to a temp file; the script prints the path at start and end.

Common issues:
- Missing Docker permissions: ensure your user is in the `docker` group (see Setup).
- Missing data caches: confirm `Benchmarks_Traces/`, `crawlPackage/database/etherScan.db`, and `parserPackage/cache/` exist.

### Basic sanity check (if logs already exist)
This verifies the table generator against `artifact_evaluation/Expected_Outputs.txt` without rerunning experiments.
```bash
python3 artifact_evaluation/table_printers.py \
  --log-dir artifact_evaluation \
  --latex artifact_evaluation/Expected_Outputs.txt \
  --table all \
  --out artifact_evaluation/tables_generated.csv
```
Expected output (stderr): `[OK] Compared with the expected outputs at /abs/path/to/Expected_Outputs.txt`

### Experiment A: SphereX overhead (RQ4-5)
Step 1: build the image.
```bash
docker build -t crossguard-artifact .
```
Meaning: builds the full analysis environment including Foundry and Python dependencies.

Step 2: run the SphereX overhead computation.
```bash
docker run --rm -v "$PWD:/app" -w /app crossguard-artifact \
  python3 spherex_reproduce/compute_gas_overhead.py
```
Meaning: computes gas overhead from cached traces and receipts.

Step 3: verify success.
Success criteria:
- stdout prints a summary with `Transactions:` and `Total ratio` lines.
- no Python exceptions (non-zero exit indicates missing caches or API failures).

### Experiment B: Foundry gas experiment (instrumentation)
Step 1: ensure `forge-std` is present.
- If the repo is a git checkout with submodules:
  - `git submodule update --init --recursive CrossGuard_foundry/lib/forge-std`
- If not, clone it:
  - `git clone --depth 1 https://github.com/foundry-rs/forge-std CrossGuard_foundry/lib/forge-std`

Step 2: run the gas experiment.
```bash
docker run --rm -v "$PWD:/app" -w /app crossguard-artifact \
  python3 CrossGuard_foundry/gas_experiment.py
```
Meaning: runs `forge test --gas-report` and compares derived deltas to `CrossGuard_foundry/expected.txt`.

Step 3: verify success.
Success criteria:
- stdout shows both "Expected" and "Actual" sections.
- no `MISMATCHES` block (if present, deltas differ from `expected.txt`).

### Experiment C: Full CrossGuard pipeline + tables
Step 1: run the full experiment suite.
```bash
docker run --rm -v "$PWD:/app" -w /app crossguard-artifact \
  python3 runFullExperiments.py
```
Meaning: runs all configurations in parallel and writes logs under `artifact_evaluation/logs/`.

Step 2: generate tables and compare against expected outputs.
```bash
docker run --rm -v "$PWD:/app" -w /app crossguard-artifact \
  python3 artifact_evaluation/table_printers.py \
    --log-dir artifact_evaluation \
    --latex artifact_evaluation/Expected_Outputs.txt \
    --table all \
    --out artifact_evaluation/tables_generated.csv
```
Meaning: parses logs, generates CSV tables, and compares them to `Expected_Outputs.txt`.

Step 3: verify success.
Success criteria:
- `artifact_evaluation/logs/` contains the expected log files.
- stderr prints `[OK] Compared with the expected outputs at /abs/path/to/Expected_Outputs.txt`.
- exit code is 0 (non-zero indicates mismatches or missing logs).

## Reusable Badge: Add a New Benchmark (Step-by-Step)
This tutorial shows how to add a new benchmark and run CrossGuard on it. It is written for reuse and repurposing: each step states what to do, what it produces, and how to check success.

### Step 0: Prepare inputs and credentials
Gather the minimum benchmark info:
- Benchmark name (folder name under `Benchmarks_Traces/CrossContract/`).
- Hack transaction hash (if applicable).
- Target contract addresses (lowercase).

Ensure `settings.toml` has valid RPC endpoints and an Etherscan API key. These are needed for trace download and labeling.

### Step 1: Register the benchmark
1) Add a short entry to `Benchmarks_Traces/CrossContract/README.md` describing the benchmark and where the trace list will live. If the file does not exist, create it.

2) Update `constraintPackage/macros.py`:
- Add the hack tx to `benchmark2hack`.
- Add target contracts to `benchmark2targetContracts`.

Optional (recommended for documentation): add a benchmark JSON under `benchmarkPackage/benchmarks/` so metadata is tracked with the rest of the dataset.

Success check:
- A simple import like `python3 -c "from constraintPackage import macros; print(macros.benchmark2hack['<BENCHMARK>'])"` should not raise a KeyError.

### Step 2: Collect transaction history
Run the collector script to produce the transaction list for the new benchmark:
```bash
python3 Benchmarks_Txs/collectCrossContract.py
```
This should write a transaction list under:
`Benchmarks_Traces/CrossContract/<BENCHMARK>/combined.txt` (and optionally `combined2.txt`).

File format (one tx per line):
`<tx_hash> <contract_addr> [contract_addr ...]`

Success check:
- `combined.txt` exists and has non-empty lines.

### Step 3: Download traces for the new benchmark
Create the trace directory and use `fetchPackage` to download traces for each tx:
```bash
mkdir -p Benchmarks_Traces/CrossContract/<BENCHMARK>/Txs

python3 - <<'PY'
from fetchPackage.fetchTrace import fetcher
import os

benchmark = "<BENCHMARK>"
txs = []
with open(f"Benchmarks_Traces/CrossContract/{benchmark}/combined.txt") as f:
    for line in f:
        if line.strip():
            txs.append(line.split()[0])

os.makedirs(f"Benchmarks_Traces/CrossContract/{benchmark}/Txs", exist_ok=True)
fe = fetcher()
for tx in txs:
    fe.storeTraceCross(benchmark, tx, FullTrace=False)
PY
```

Traces are stored as:
`Benchmarks_Traces/CrossContract/<BENCHMARK>/Txs/<tx>.json.gz`

Success check:
- The number of `.json.gz` files roughly matches the number of txs in `combined.txt`.
- Files are non-zero size.

### Step 4: Parse traces into invocation trees
Run the parser over the new benchmark:
```bash
python3 -c "import mainCross; mainCross.main('<BENCHMARK>')"
```

This produces invocation trees under:
`parserPackage/cache/<BENCHMARK>/<block>.json.gz`

Success check:
- New cache files appear under `parserPackage/cache/<BENCHMARK>/`.

### Step 5: Extract function-access data (CFI inputs)
This step builds the `functionAccess` cache from invocation trees. You can run it two ways:

Option A (temporary edit): edit `constraintPackage/functionAccess_FullyOnchainVersion.py` so `listBenchmark` contains only `<BENCHMARK>`, then run:
```bash
python3 constraintPackage/functionAccess_FullyOnchainVersion.py --pruneRuntimeReadOnly --pruneCache --pruneERC20 --pruneRAW
```

Option B (one-off call without editing):
```bash
python3 - <<'PY'
from constraintPackage.functionAccess_FullyOnchainVersion import executeOnce
executeOnce(["<BENCHMARK>"], True, True, True, True, None)
PY
```

Output:
`constraintPackage/cache/functionAccess/<BENCHMARK>/<block>.json`

Success check:
- The functionAccess cache exists and includes entries for the benchmark txs.

### Step 6: Label transactions
Label the transactions to categorize them and collect Etherscan labels:
```bash
python3 - <<'PY'
from labelTransactions.transactionLabeling import labelTransaction
labelTransaction("<BENCHMARK>")
PY
```

This prints label results to stdout. Use `labelPackage/readLabels.py` as a helper if you need to resolve or normalize labels programmatically.

Success check:
- The script completes without errors and prints labeled contract summaries.

### Step 7: Run CrossGuard on the new benchmark
With traces, invocation trees, and functionAccess caches in place, rerun the CrossGuard pipeline for the new benchmark (same as Step 5) or integrate it into `runFullExperiments.py` if you want it included in the full tables.

Success check:
- Logs under `artifact_evaluation/logs/` include the new benchmark with counts and gas overhead lines.

## Mapping to Paper Results
See `artifact_evaluation/ae_reproduction_mapping.md` and `artifact_evaluation/ae_validation_targets.md` for detailed mappings. Summary:

- Table 1 (Study / RQ1+RQ3): generated from `artifact_evaluation/logs/RR_RE_ERC20_RAW.txt` via `table_printers.py`.
- Table 2 (Ablation + Gas + Feedback / RQ2+RQ4-5): generated from the full set of `artifact_evaluation/logs/*.txt` via `table_printers.py`.
- Table 3 (CrossGuard vs Trace2Inv / RQ6): generated from `artifact_evaluation/logs/trace2inv0_*` and `trace2inv1_*`.
- Instrumentation table (`tables/instrumentation.tex`): not generated by scripts in this repo; see source code under `constraintPackage/` for the implementation.

## Known Gaps and Manual Checks
These items are documented in `artifact_evaluation/ae_reproduction_mapping.md` as not automatically derivable:
- Bypassability columns in Table 2 (manual validation).
- Dataset split 21/8/8 by source (manual from benchmark metadata).
- Instrumentation table rendering (`tables/instrumentation.tex`).

## Directory Overview
- `runFullExperiments.py`: runs the full CrossGuard and Trace2Inv experiment suite.
- `artifact_evaluation/`: table generation, expected outputs, and validation targets.
- `spherex_reproduce/`: SphereX overhead computation.
- `CrossGuard_foundry/`: Foundry tests and gas experiment script.

If you need a different execution flow (e.g., native Python or custom RPCs), update `settings.toml` and re-run the commands above.
