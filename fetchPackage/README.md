# fetchPackage

This folder is the bridge between our pipeline and an Ethereum node. It fetches transaction traces, prunes them to keep files small, and writes them in a cache-friendly format.

## What these scripts do

- `fetchTrace.py` calls `debug_traceTransaction` through Web3, prunes stack/memory fields, and stores the result as compressed files. It reads RPC endpoints from `settings.toml` and cycles through them for load balancing.
- `StackCarpenter.py` provides opcode stack length helpers so the trace pruning logic keeps only the stack items we need.

## How it fits in the pipeline

- This stage runs before analysis. The rest of the code assumes traces already exist on disk in the expected cache layout.
- If your RPC endpoint is slow or rate-limited, this is the step that will feel it. Adjust `settings.toml` accordingly.

## Notes

- These scripts rely on `settings.toml` at the repo root for RPC provider URLs.
- Outputs are written using gzip + pickle (see `utilsPackage/compressor.py`).
