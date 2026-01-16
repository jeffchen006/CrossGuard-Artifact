# Artifact Abstract

This artifact packages the code, datasets, and scripts needed to reproduce the experimental results of the CrossGuard paper. It includes cached traces and receipts, labeling data, and analysis utilities, as well as a complete experiment driver and a table generator that compares outputs to expected results. The goal is to let reviewers rerun the pipeline end to end and verify the numbers reported in the paper, including the study table, ablation and gas results, and the CrossGuard vs Trace2Inv comparison.

The artifact is hosted at [GitHub - CrossGuard Artifact Repository](https://github.com/jeffchen006/CrossGuard-artifact) and archived on Zenodo at [Zenodo - CrossGuard Artifact](https://zenodo.org/records/18262998), with a DOI of [10.5281/zenodo.18262998](https://doi.org/10.5281/zenodo.18262998).

## What the artifact contains

- A full experiment runner: `runFullExperiments.py` executes all CrossGuard configurations (baseline through feedback windows) and the Trace2Inv comparison variants, then writes logs under `artifact_evaluation/logs/`.
- A results extractor and checker: `artifact_evaluation/table_printers.py` parses the logs, generates `artifact_evaluation/tables_generated.csv`, and compares it against `artifact_evaluation/Expected_Outputs.txt`.
- Two targeted experiments used in the paper:
  - `spherex_reproduce/compute_gas_overhead.py` computes SphereX-related gas overhead numbers.
  - `CrossGuard_foundry/gas_experiment.py` runs Foundry-based tests to validate instrumentation overhead.
- Datasets and metadata:
  - `Benchmarks_Traces/` contains per-benchmark transaction lists used to drive the trace pipeline.
  - `constraintPackage/` and `parserPackage/` contain cached analysis artifacts and decoded traces (large).
  - `labelPackage/` and `labelTransactions/` provide labelled contracts and scripts.
- Dataset packaging by source:
  - Zenodo archive includes the raw `constraintPackage/cache/functionAccess/` cache.
  - GitHub clone uses split zip archives under `constraintPackage/cache/functionAccess_zips/` due to size limits; unpack with `scripts/unpack_functionAccess_zips.sh` or run `./docker_eval_run.sh` (auto-unpacks when zips are present).

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

## Summary

This artifact is intended to be an executable, reproducible package for validating the CrossGuard evaluation. With the provided datasets, the experiment runner, and the comparison scripts, reviewers can regenerate the key tables and confirm that the reported numbers are consistent with the code and data included here.
