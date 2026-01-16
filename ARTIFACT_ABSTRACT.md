# Artifact Abstract

This artifact packages the code, datasets, and scripts needed to reproduce the experimental results of the CrossGuard paper. It includes cached traces and receipts, labeling data, and analysis utilities, as well as a complete experiment driver and a table generator that compares outputs to expected results. The goal is to let reviewers rerun the pipeline end to end and verify the numbers reported in the paper, including the study table, ablation and gas results, and the CrossGuard vs Trace2Inv comparison.

## What the artifact contains

- A full experiment runner: `runFullExperiments.py` executes all CrossGuard configurations (baseline through feedback windows) and the Trace2Inv comparison variants, then writes logs under `artifact_evaluation/logs/`.
- A results extractor and checker: `artifact_evaluation/table_printers.py` parses the logs, generates `artifact_evaluation/tables_generated.csv`, and compares it against `artifact_evaluation/Expected_Outputs.txt`.
- Two targeted experiments used in the paper:
  - `spherex_reproduce/compute_gas_overhead.py` computes SphereX-related gas overhead numbers.
  - `CrossGuard_foundry/gas_experiment.py` runs Foundry-based tests to validate instrumentation overhead.
- Datasets and metadata:
  - `Benchmarks_Traces/` contains per-benchmark transaction lists used to drive the trace pipeline.
  - `constraintPackage/` and `parserPackage/` contain cached analysis artifacts and decoded traces (large).
  - `labelPackage/` and `labelTransactions/` provide labeling inputs and scripts.

## How results map to the paper

- Study table (RQ1/RQ3): generated from CrossGuard logs in `artifact_evaluation/logs/` and parsed by `table_printers.py`.
- Ablation and gas table (RQ2/RQ4-5): generated from the full set of CrossGuard logs (baseline through feedback windows).
- Comparison table (RQ6): generated from Trace2Inv comparison logs.

The detailed mapping is documented in `artifact_evaluation/ae_reproduction_mapping.md`, and expected outputs are listed in `artifact_evaluation/Expected_Outputs.txt`.

## Requirements and access

- Hardware: multi-core CPU recommended, 32 GB RAM recommended, and at least 80 GB free disk space.
- Software: Docker Engine 24+ (tested with Docker 28) on a Linux host.
- Network and credentials:
  - RPC endpoints with trace support and an Etherscan API key configured in `settings.toml`.
  - Outbound network access to those services.

## High-level usage

1) Build the Docker image:

```bash
docker build -t crossguard-artifact .
```

2) Run the three main experiments:

```bash
# SphereX overhead
docker run --rm -v "$PWD:/app" -w /app crossguard-artifact \
  python3 spherex_reproduce/compute_gas_overhead.py

# Foundry gas experiment
docker run --rm -v "$PWD:/app" -w /app crossguard-artifact \
  python3 CrossGuard_foundry/gas_experiment.py

# Full pipeline
docker run --rm -v "$PWD:/app" -w /app crossguard-artifact \
  python3 runFullExperiments.py
```

3) Generate and verify tables:

```bash
docker run --rm -v "$PWD:/app" -w /app crossguard-artifact \
  python3 artifact_evaluation/table_printers.py \
    --log-dir artifact_evaluation \
    --latex artifact_evaluation/Expected_Outputs.txt \
    --table all \
    --out artifact_evaluation/tables_generated.csv
```

Expected result: the script prints a success message indicating the outputs match the expected tables, and exits with status 0.

## Limitations and manual checks

Some paper claims are not fully automated by scripts in this repository and require manual inspection, including bypassability labels in the ablation table, the dataset split count (21/8/8), and the instrumentation mapping table. These are tracked in `artifact_evaluation/ae_validation_targets.md`.

## Summary

This artifact is intended to be an executable, reproducible package for validating the CrossGuard evaluation. With the provided datasets, the experiment runner, and the comparison scripts, reviewers can regenerate the key tables and confirm that the reported numbers are consistent with the code and data included here.
